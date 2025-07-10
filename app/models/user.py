from sqlmodel import Field, SQLModel

#define user table
class User(SQLModel, table=True):
    __tablename__ = "users" #name the table users

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    full_name: str | None = None
    hashed_password: str
    disabled: bool = Field(default=False)