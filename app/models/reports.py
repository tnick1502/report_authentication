from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReportBase(BaseModel):
    object_number: str = Field(..., max_length=250)
    laboratory_number: str = Field(..., max_length=100)
    test_type: str = Field(..., max_length=100)
    data: Optional[dict] = None
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
    data: Optional[dict] = None
    active: bool

