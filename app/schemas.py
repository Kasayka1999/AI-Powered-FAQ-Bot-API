from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    username: str = Field(min_length=0,  max_length=20)
    email: str
    full_name: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool
