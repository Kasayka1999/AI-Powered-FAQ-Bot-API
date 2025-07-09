from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base, engine

#define user table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)


# create a table
Base.metadata.create_all(engine)