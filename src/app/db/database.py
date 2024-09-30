from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import configs

engine = create_async_engine(
    configs.database_url,
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_recycle=3600
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()
