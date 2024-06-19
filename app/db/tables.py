from sqlalchemy import Column, String, Integer, Date, JSON, Boolean, ForeignKey, BigInteger, \
    DateTime, Index, Enum
from sqlalchemy.orm import relationship
from db.database import Base
import enum

class LicenseLevel(enum.Enum):
    STANDART = 'Standart'
    PRO = 'Pro'
    ENTERPRISE = 'Enterprise'

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    mail = Column(String(50), unique=True)
    phone = Column(BigInteger, unique=True)
    password_hash = Column(String(60))
    active = Column(Boolean)
    is_superuser = Column(Boolean)
    organization = Column(String(50))
    organization_url = Column(String(50))
    license_level = Column(Enum(LicenseLevel))
    license_end_date = Column(Date)
    license_update_date = Column(Date)
    limit = Column(Integer)

    reports = relationship("Reports", backref="report")


class Reports(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    datetime = Column(DateTime)
    laboratory_number = Column(String(100))
    test_type = Column(String(100))
    object_number = Column(String(250))
    data = Column(JSON, nullable=True, default=None)
    active = Column(Boolean)


class Files(Base):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(String, ForeignKey('reports.id'), index=True)
    filename = Column(String)
    link = Column(String)


class TestTypeFiles(Base):
    __tablename__ = "test_type_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    test_type = Column(String(100))
    filename = Column(String)
    link = Column(String)


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(String, ForeignKey('reports.id'), index=True)
    client_ip = Column(String)
    datetime = Column(DateTime)


ix_create_date = Index('ix_create_date', Reports.datetime, postgresql_using='btree')
ix_object_number = Index('ix_object_number', Reports.object_number, postgresql_using='btree')
ix_files_report_id = Index('ix_files_report_id', Files.report_id, postgresql_using='btree')
ix_statistics_datetime = Index('ix_statistics_datetime', Statistics.datetime, postgresql_using='btree')