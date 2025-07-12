from fastapi import FastAPI
from app.api.v1.router import master_router
from app.database.database import create_db_and_tables


app = FastAPI()

app.include_router(master_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
