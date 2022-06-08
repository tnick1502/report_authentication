from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import configs

Base = declarative_base()

engine = create_async_engine(
        configs.database_url,
        echo=True,
    )
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
from sqlalchemy import Column, String, Integer, Date, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    mail = Column(String, unique=True)
    password_hash = Column(String)
    is_sureruser = Column(Boolean, nullable=True)
    organization = Column(String)
    limit = Column(Integer)
    organization_url = Column(String, nullable=True)