from pydantic import BaseModel, Field

class FileBase(BaseModel):
    report_id: str = Field(..., description="Уникальный идентификатор отчета")
    filename: str = Field(..., description="Название файла")

class File(FileBase):
    id: int = Field(..., description="Уникальный идентификатор записи файла")
    link: str = Field(..., description="URL-ссылка на файл")

    class Config:
        from_attributes = True  # Обеспечивает совместимость с ORM моделями.

class FileCreate(FileBase):
    link: str = Field(..., description="URL-ссылка на файл, который нужно создать")

class TestTypeFileBase(BaseModel):
    test_type: str = Field(..., description="Тип испытания")
    filename: str = Field(..., description="Название файла испытания")

class TestTypeFile(TestTypeFileBase):
    id: int = Field(..., description="Уникальный идентификатор файла типа теста.")
    user_id: int = Field(..., description="Идентификатор пользователя, связанного с типом теста.")

    class Config:
        from_attributes = True  # Обеспечивает совместимость с ORM моделями.

class TestTypeFileCreate(TestTypeFileBase):
    link: str = Field(..., description="URL-ссылка на файл типа теста, который нужно создать.")
