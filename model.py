from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Produit(Base):
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    description = Column(String)
    prix = Column(Integer, nullable=False)
    dispo = Column(Boolean, default=True)
    image_url = Column(String)
    quantite = Column(Integer, default=0)

    commandes_items = relationship("OrderItem", back_populates="produit")


class Order(Base):
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String)
    tel = Column(String)
    table = Column(String)
    statuts = Column(String)

    items = relationship("OrderItem", back_populates="commande", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "commande_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("commandes.id"))
    product_id = Column(Integer, ForeignKey("produits.id"))
    quantite = Column(Integer)

    commande = relationship("Order", back_populates="items")
    produit = relationship("Produit", back_populates="commandes_items")
