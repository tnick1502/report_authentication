from pydantic import BaseModel, Field
from datetime import date
from db.tables import LicenseLevel

class BaseUser(BaseModel):
    username: str = Field(..., max_length=50, description="Имя пользователя (максимум 50 символов).")
    mail: str = Field(..., max_length=50, description="Электронная почта пользователя (максимум 50 символов).")
    is_superuser: bool = Field(..., description="Флаг суперпользователя.")
    organization: str = Field(..., max_length=50, description="Название организации (максимум 50 символов).")
    phone: int = Field(..., description="Телефонный номер пользователя.")
    active: bool = Field(..., description="Статус активности пользователя.")
    organization_url: str = Field(..., max_length=50, description="URL-адрес организации (максимум 50 символов).")
    license_level: LicenseLevel = Field(..., description="Уровень лицензии пользователя.")
    license_end_date: date = Field(..., description="Дата окончания лицензии.")
    license_update_date: date = Field(..., description="Дата обновления лицензии.")
    limit: int = Field(..., description="Лимит операций для пользователя.")

class UserCreate(BaseUser):
    password: str = Field(..., max_length=50, description="Пароль для создания пользователя.")

class UserUpdate(UserCreate):
    """Модель для обновления данных пользователя."""
    pass

class User(BaseUser):
    id: int = Field(..., description="Уникальный идентификатор пользователя.")
    password_hash: str = Field(..., description="Хеш пароля пользователя.")

    class Config:
        from_attributes = True  # Обеспечивает совместимость с ORM моделями.

class LicenseUpdate(BaseModel):
    license_level: LicenseLevel = Field(..., description="Новый уровень лицензии.")
    license_end_date: date = Field(..., description="Новая дата окончания лицензии.")
    license_update_date: date = Field(..., description="Новая дата обновления лицензии.")
    limit: int = Field(..., description="Новый лимит операций.")

class Token(BaseModel):
    access_token: str = Field(..., description="Токен доступа.")
    token_type: str = Field(default='bearer', description="Тип токена (по умолчанию 'bearer').")