from pydantic import BaseModel, Field
from datetime import date
from db.tables import LicenseLevel

class BaseUser(BaseModel):
    username: str= Field(..., max_length=50)
    mail: str = Field(..., max_length=50)
    is_superuser: bool
    organization: str = Field(..., max_length=50)
    phone: int
    active: bool
    organization_url: str = Field(..., max_length=50)
    license_level: LicenseLevel
    license_end_date: date
    license_update_date: date
    limit: int

class UserCreate(BaseUser):
    password: str = Field(..., max_length=50)

class UserUpdate(UserCreate):
    pass

class User(BaseUser):
    id: int
    password_hash: str

    class Config:
        orm_mode = True

class LicenseUpdate(BaseModel):
    license_level: LicenseLevel
    license_end_date: date
    license_update_date: date
    limit: int

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'