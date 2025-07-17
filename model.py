from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    description = Column(String)
    prix = Column(Integer, nullable=False)
    dispo = Column(Boolean, default=True)
    image_url = Column(String)
    quantite = Column(Integer)


class OrderItem(Base):
    __tablename__ = "order_itemss"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orderss.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantite = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "orderss"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    tel = Column(String, nullable=True)
    table = Column(String, nullable=True)
    statuts = Column(String, nullable=True)

    items = relationship("OrderItem", back_populates="order")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    password = Column(String)
