from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = 'sqlite:///./database.db'

#Create database engine
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

#Create a session
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


Base = declarative_base()

#dependency with yield
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
