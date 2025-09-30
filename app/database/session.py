from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import db_settings

# Create a database engine to connect with database
# ensure db_settings.POSTGRES_URL is postgresql+asyncpg://... or plain but we'll force ssl here
engine = create_async_engine(
    url=db_settings.POSTGRES_URL,
    echo=True,
    #connect_args={"ssl": True},  # force TLS for asyncpg
)


async def create_db_tables():
    async with engine.begin() as connection:
        # Ensure models are imported so SQLModel is aware of tables
        from app.models.user import User 
        from app.models.organization import Organization  
        from app.models.documents import Documents, DocumentChunk

        # Ensure pgvector extension exists BEFORE creating tables using vector type
        await connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")

        # Create tables
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)