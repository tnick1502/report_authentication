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
    is_superuser = Column(Boolean)
    organization = Column(String)
    organization_url = Column(String)

    license = relationship("Licenses", backref="license", uselist=False)
    reports = relationship("Reports", backref="report")

class Licenses(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    license_level = Column(String)
    license_end_date = Column(Date)
    license_update_date = Column(Date)
    limit = Column(Integer)

class Reports(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    date = Column(Date)
    object_number = Column(String)
    data = Column(JSON)
    active = Column(Boolean)