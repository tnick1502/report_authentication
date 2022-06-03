from sqlalchemy import (
    Column,
    Date,
    Float,
    String,
    Integer,
    Boolean,
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    mail = Column(String, unique=True)
    password_hash = Column(String)
    is_superuser = Column(Boolean, nullable=True)
    organization = Column(String)
    limit = Column(Integer)
    organization_url = Column(String, nullable=True)


class Report(Base):
    __tablename__ = 'reports'

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    date = Column(Date, nullable=True)
    object_number = Column(String)
    data = Column(JSON)
