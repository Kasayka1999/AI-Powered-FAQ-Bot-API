from typing import Annotated
from sqlmodel import Session, create_engine, SQLModel
from fastapi import Depends



DATABASE_URL = 'sqlite:///./database.db'

#Create database engine
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})


#dependency with yield
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)