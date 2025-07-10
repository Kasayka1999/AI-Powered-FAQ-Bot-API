from fastapi import FastAPI
from app.routers import registration, login
from app.database.database import create_db_and_tables


app = FastAPI()

app.include_router(login.router)
app.include_router(registration.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
