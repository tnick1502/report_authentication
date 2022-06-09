from sqlalchemy import Column, String, Integer, Date, JSON, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from db.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    mail = Column(String, unique=True)
    phone = Column(BigInteger, unique=True)
    password_hash = Column(String)
    active = Column(Boolean)
    is_superuser = Column(Boolean, nullable=True)
    organization = Column(String)
    limit = Column(Integer)
    organization_url = Column(String, nullable=True)

class Reports(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    date = Column(Date)
    object_number = Column(String)
    data = Column(JSON)
    active = Column(Boolean)

    user = relationship('Users', backref='reports')