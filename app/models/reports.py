from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ReportBase(BaseModel):
    object_number: str
    laboratory_number: str
    test_type: str
    data: dict
    active: bool


class Report(ReportBase):
    id: str
    user_id: int
    datetime: datetime
    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    data: dict
    active: bool

