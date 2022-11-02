from pydantic import BaseModel
from datetime import date
from enum import Enum

class LicenseLevel(str, Enum):
    STANDART = 'standart'
    UPPER = 'upper'
    PRO = "pro"

class LicenseBase(BaseModel):
    license_level: LicenseLevel
    license_end_date: date
    license_update_date: date
    limit: int

class License(LicenseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class LicenseCreate(LicenseBase):
    pass

class LicenseUpdate(LicenseBase):
    user_id: int

