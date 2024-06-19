from db.database import async_session
from services.reports import ReportsService
from services.users import UsersService
from services.statistics import StatisticsService

async def get_report_service():
    async with async_session() as session:
        async with session.begin():
            yield ReportsService(session)

async def get_users_service():
    async with async_session() as session:
        async with session.begin():
            yield UsersService(session)

async def get_statistics_service():
    async with async_session() as session:
        async with session.begin():
            yield StatisticsService(session)
