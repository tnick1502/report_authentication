from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReportBase(BaseModel):
    date: date
    object_number: str
    data: dict


class Report(ReportBase):
    id: str
    user_id: str
    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

