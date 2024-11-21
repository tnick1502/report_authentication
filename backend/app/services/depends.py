import asyncio
from aiobotocore.session import get_session
from botocore.config import Config

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
                await session.commit()
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
    config = Config(
        connect_timeout=1000,  # Таймаут соединения
        read_timeout=1000,  # Таймаут чтения
        retries={"max_attempts": 3, "mode": "adaptive"}  # Повтор попыток
    )
    async with session.create_client(
            's3',
            endpoint_url=configs.endpoint_url,
            region_name=configs.region_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            aws_access_key_id=configs.aws_access_key_id,
            config=config
    ) as client:
        try:
            yield S3Service(client)
        except Exception as e:
            raise e
        finally:
            await client.close()

# Объединяем все сервисы в единый паттерн
async def get_unit_of_work():
    async with async_session() as session:
        async with session.begin():
            try:
                report_service = ReportsService(session)
                user_service = UsersService(session)
                statistics_service = StatisticsService(session)

                s3_session = get_session()  # Создаем сессию для работы с AWS S3
                s3_client = None
                async with s3_session.create_client(
                        's3',
                        endpoint_url=configs.endpoint_url,
                        region_name=configs.region_name,
                        aws_secret_access_key=configs.aws_secret_access_key,
                        aws_access_key_id=configs.aws_access_key_id
                ) as s3_client:
                    s3_service = S3Service(s3_client)

                    yield {
                        'report_service': report_service,
                        'user_service': user_service,
                        'statistics_service': statistics_service,
                        's3_service': s3_service
                    }

                    await session.commit()

            except Exception as e:
                await session.rollback()  # Откатываем транзакцию при ошибке
                raise e
            finally:
                if s3_client is not None:
                    await s3_client.close()
                await session.close()
