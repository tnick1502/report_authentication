from pydantic import BaseModel

class BaseUser(BaseModel):
    username: str
    mail: str
    is_superuser: bool
    organization: str
    limit: int
    organization_url: str

class UserCreate(BaseUser):
    password: str

class UserUpdate(BaseUser):
    username: str
    mail: str
    password: str
    organization: str
    limit: int
    organization_url: str

class User(BaseUser):
    id: int
    password_hash: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'