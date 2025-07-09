from fastapi import FastAPI
from app.routers import registration, auth
from app.models import create_db_and_tables


app = FastAPI()

app.include_router(auth.router)
app.include_router(registration.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
