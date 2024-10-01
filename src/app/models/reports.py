from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReportBase(BaseModel):
    object_number: str = Field(..., max_length=250, description="Номер объекта (максимум 250 символов)")
    laboratory_number: str = Field(..., max_length=100, description="Лабораторный номер (максимум 100 символов)")
    test_type: str = Field(..., max_length=100, description="Тип испытания (максимум 100 символов)")
    data: Optional[dict] = Field(default=None, description="Дополнительные данные в формате словаря")
    active: bool = Field(..., description="Статус активности отчета")

class Report(ReportBase):
    id: str = Field(..., description="Уникальный идентификатор отчета")
    user_id: int = Field(..., description="Идентификатор пользователя, создавшего отчет")
    datetime: datetime

    class Config:
        from_attributes = True  # Обеспечивает совместимость с ORM моделями.

class ReportCreate(ReportBase):
    """Модель для создания нового отчета."""
    pass

class ReportUpdate(BaseModel):
    data: Optional[dict] = Field(default=None, description="Дополнительные данные для обновления отчета")
    active: bool = Field(..., description="Новый статус активности отчета")
