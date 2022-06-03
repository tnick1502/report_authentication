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

class User(BaseUser):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'