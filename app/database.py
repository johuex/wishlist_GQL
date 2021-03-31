import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config

engine = create_engine(
Config.SQLALCHEMY_DATABASE_URL
#    Config.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = databases.Database(Config.SQLALCHEMY_DATABASE_URL)

Base = declarative_base()


