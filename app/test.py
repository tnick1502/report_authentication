from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
import hashlib


print(hashlib.sha1(f"{'-'} {'Э1-1/-/ТС'} {'test'} {1}".encode("utf-8")).hexdigest())