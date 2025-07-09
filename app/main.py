from fastapi import FastAPI
from app.routers import auth, registration


app = FastAPI()

app.include_router(auth.router)
app.include_router(registration.router)

