from pydantic import BaseModel

class FileBase(BaseModel):
    report_id: str
    filename: str

class File(FileBase):
    id: int
    link: str
    class Config:
        orm_mode = True

class FileCreate(FileBase):
    link: str