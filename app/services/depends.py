import asyncio
from aiobotocore.session import get_session

from config import configs
from db.database import async_session
from services.reports import ReportsService
from services.users import UsersService
from services.statistics import StatisticsService
from services.s3 import S3Service

# Универсальная функция для работы с асинхронной сессией
async def get_service(service_class):
    async with async_session() as session:
        async with session.begin():
            try:
                yield service_class(session)
            except Exception as e:
                await session.rollback()  # Откатываем транзакцию при ошибке
                raise e
            finally:
                await session.close()  # Закрываем сессию

# Получение сервиса отчетов
async def get_report_service():
    async for service in get_service(ReportsService):
        yield service

# Получение сервиса пользователей
async def get_users_service():
    async for service in get_service(UsersService):
        yield service

# Получение сервиса статистики
async def get_statistics_service():
    async for service in get_service(StatisticsService):
        yield service

# Работа с S3 через aiobotocore
async def get_s3_service():
    session = get_session()  # Создаем сессию для работы с AWS S3
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
            raise e
        finally:
            await client.close()