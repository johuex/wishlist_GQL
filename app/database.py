from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal.configure(bind=engine)
db_session = SessionLocal()  # наша сессия, через которую мы можем query или add


def commit_with_check(db_s):
    try:
        db_s.commit()
    except:
        db_s.rollback()


Base = declarative_base()


