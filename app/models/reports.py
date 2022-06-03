from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReportBase(BaseModel):
    user_id: int
    date: date
    object_number: str
    data: dict


class Report(ReportBase):
    id: str
    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    id: Optional[str] = ""
    laboratory_number: Optional[str] = ""
    test_type: Optional[str] = ""

