from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    email: str
    full_name: str | None = None
    password: str  # This will be hashed before storing
