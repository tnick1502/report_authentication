import asyncio
from aiobotocore.session import get_session

from config import configs
from db.database import async_session
from services.reports import ReportsService
from services.users import UsersService
from services.statistics import StatisticsService
from services.s3 import S3Service


async def get_report_service():
    async with async_session() as session:
        async with session.begin():
            try:
                yield ReportsService(session)
            except Exception as e:
                await session.rollback()
                print(e)

async def get_users_service():
    async with async_session() as session:
        async with session.begin():
            try:
                yield UsersService(session)
            except Exception as e:
                await session.rollback()
                print(e)

async def get_statistics_service():
    async with async_session() as session:
        async with session.begin():
            try:
                yield StatisticsService(session)
            except Exception as e:
                await session.rollback()
                print(e)

async def get_s3_service():
    bucket = configs.bucket
    session = get_session()
    async with session.create_client(
            's3',
            endpoint_url=configs.endpoint_url,
            region_name=configs.region_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            aws_access_key_id=configs.aws_access_key_id
    ) as client:
        try:
            yield S3Service(client)
        except Exception as e:
            await session.rollback()
            print(e)