from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReportBase(BaseModel):
    object_number: str
    data: dict
    active: bool


class Report(ReportBase):
    id: str
    user_id: int
    date: date
    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

