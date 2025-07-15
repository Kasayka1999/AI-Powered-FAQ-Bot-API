from fastapi import FastAPI
from app.api.v1.router import master_router
from app.database.database import create_db_and_tables
from scalar_fastapi import get_scalar_api_reference


app = FastAPI()

app.include_router(master_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )