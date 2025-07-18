from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from model import Product
from database import Egine,Base,Session_Local
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from model import Order,OrderItem
from sqlalchemy.orm import joinedload

from pydantic import BaseModel
from typing import List, Optional
from datetime import date
Base.metadata.create_all(bind=Egine)

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
# Autoriser le frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:3000"] pour sécuriser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

class ProductBase(BaseModel):
    nom: str
    description: str
    prix: int
    dispo: bool = True
    image_url: str 
    quantite: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True


def get_db():
    db = Session_Local()
    try:
        yield db

    finally:
        db.close()

class OrderItemCreate(BaseModel):
    product_id: int
    quantite: int

class OrderItemRead(OrderItemCreate):
    id: int

    class Config:
        orm_mode = True




class OrderCreate(BaseModel):
    client_name: str
    tel: Optional[str]
    table: Optional[str]
    statuts: str
    items: List[OrderItemCreate]

class OrderRead(BaseModel):
    id: int
    client_name: str
    tel: Optional[str]
    table: Optional[str]
    statuts: str
    items: List[OrderItemRead]

    class Config:
        orm_mode = True

@app.post("/Restau/Produit/", response_model=ProductRead)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/Restau/Produit/", response_model=list[ProductRead])
def read_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/Restau/Produit/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return product

@app.put("/Restau/Produit/{product_id}", response_model=ProductRead)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).get(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    for field, value in product.dict().items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/Restau/Produit/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).get(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    db.delete(db_product)
    db.commit()
    return {"message": "Produit supprime"}
# -----------------------
# POST /orders/
# -----------------------
@app.post("/Restau/orders/")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        client_name=order.client_name,
        tel=order.tel,
        table=order.table,
        statuts=order.statuts
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantite=item.quantite
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return {"message": "Commande créée avec succès", "order_id": db_order.id}

# -----------------------
# GET /orders/
# -----------------------

@app.get("/Restau/orders/", response_model=List[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.items)).all()
    return orders

@app.get("/Restau/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).options(joinedload(Order.items)).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order


# -----------------------
# PUT /orders/{order_id}
# -----------------------
@app.put("/Restau/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).get(order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    db_order.client_name = order.client_name
    db_order.tel = order.tel
    db_order.table = order.table
    db_order.date = order.date
    db_order.statuts = order.statuts

    # Supprime les anciens items
    db.query(OrderItem).filter(OrderItem.order_id == db_order.id).delete()
    db.commit()

    # Ajoute les nouveaux items
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantite=item.quantite
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order

# -----------------------
# DELETE /orders/{order_id}
# -----------------------
@app.delete("/Restau/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).get(order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    db.delete(db_order)
    db.commit()
    return {"message": "Commande supprimée"}