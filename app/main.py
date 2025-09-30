import logging
"""
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)"""


from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import master_router
from app.database.session import create_db_tables
from scalar_fastapi import get_scalar_api_reference


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(
    title="AI-Powered FAQ Bot API",
    # Server start/stop listener
    lifespan=lifespan_handler,
)


app.include_router(master_router)



# Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )


@app.get("/")
def root():
    # Nice for quick sanity checks and to reduce 404s on "/"
    return {"ok": True, "docs": "/docs", "health": "/healthz"}


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}