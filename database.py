from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Database_URL = "sqlite:///./restaurant.db"

Egine = create_engine(Database_URL, connect_args={"check_same_thread": False})

Session_Local = sessionmaker(autocommit=False,autoflush=False,bind=Egine)

Base = declarative_base()