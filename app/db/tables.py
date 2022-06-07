from sqlalchemy import Column, String, Integer, Date, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Reports(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    date = Column(Date)
    object_number = Column(String)
    data = Column(JSON)
    active = Column(Boolean)

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