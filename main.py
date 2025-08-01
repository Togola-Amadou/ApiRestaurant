from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
from database import Base, Egine, Session_Local
from model import Produit, Order, OrderItem

Base.metadata.create_all(bind=Egine)

app = FastAPI()

# CORS pour React ou mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static images
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------- SCHEMAS -------------------

class ProduitBase(BaseModel):
    nom: str
    description: Optional[str]
    prix: int
    dispo: bool = True
    image_url: Optional[str]
    quantite: int

class ProduitCreate(ProduitBase): pass
class ProduitRead(ProduitBase):
    id: int
    class Config:
        orm_mode = True

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

# ----------------- UTILS -------------------
def get_db():
    db = Session_Local()
    try:
        yield db
    finally:
        db.close()

# ----------------- UPLOAD -------------------
@app.post("/upload-image/")
def upload(file: UploadFile = File(...)):
    path = f"static/{file.filename}"
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/static/{file.filename}"}

# ----------------- PRODUITS -------------------
@app.post("/Restau/Produit/", response_model=ProduitRead)
def create_produit(produit: ProduitCreate, db: Session = Depends(get_db)):
    db_produit = Produit(**produit.dict())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit

@app.get("/Restau/Produit/", response_model=List[ProduitRead])
def get_produits(db: Session = Depends(get_db)):
    return db.query(Produit).all()


@app.delete("/Restau/Produit/{id}")
def delete_produit(id: int, db: Session = Depends(get_db)):
    produit = db.query(Produit).get(id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    db.delete(produit)
    db.commit()
    return {"message": "Produit supprimé avec succès"}  
# ----------------- COMMANDES -------------------
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
        product = db.query(Produit).get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produit introuvable")
        if product.quantite < item.quantite:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {product.nom}")
        product.quantite -= item.quantite
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantite=item.quantite
        )
        db.add(db_item)

    db.commit()
    return {"message": "Commande créée avec succès", "order_id": db_order.id}

@app.get("/Restau/orders/", response_model=List[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).options(joinedload(Order.items)).all()


from fastapi import Query

@app.patch("/Restau/Produit/{id}/stock")
def update_stock(id: int, quantite: int = Query(...), db: Session = Depends(get_db)):
    produit = db.query(Produit).get(id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    produit.quantite = quantite
    db.commit()
    db.refresh(produit)
    return {"message": f"Quantité du produit {produit.nom} mise à jour à {produit.quantite}"}
