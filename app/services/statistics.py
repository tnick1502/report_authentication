import datetime
from typing import List, Optional
from sqlalchemy.sql import extract
from sqlalchemy.future import select
from sqlalchemy import delete, func
from sqlalchemy.orm import Session

import db.tables as tables
from modules.exceptions import exception_not_found


class StatisticsService:
    def __init__(self, session: Session):
        """Инициализация сервиса статистики с сессией базы данных"""
        self.session = session

    async def get_by_report_id(self, report_id: str) -> List[tables.Statistics]:
        """Получение статистики по идентификатору отчета"""
        result = await self.session.execute(
            select(tables.Statistics).filter_by(report_id=report_id)
        )
        statistics = result.scalars().all()

        if not statistics:
            raise exception_not_found
        return statistics

    async def get_by_date(
            self,
            user_id: int,
            month: Optional[int] = None,
            year: Optional[int] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[tables.Statistics]:
        """Получение статистики по дате с возможностью фильтрации по пользователю, месяцу и году"""
        filters = []

        if month:
            filters.append(extract('month', tables.Statistics.datetime) == month)
        if year:
            filters.append(extract('year', tables.Statistics.datetime) == year)

        filters.append(tables.Reports.user_id == user_id)

        result = await self.session.execute(
            select(tables.Statistics).
            join(
                tables.Reports,
                tables.Reports.id == tables.Statistics.report_id,
                isouter=True
            ).
            filter(*filters).
            offset(offset).
            limit(limit)
        )

        statistics = result.scalars().all()

        if not statistics:
            raise exception_not_found
        return statistics

    async def count(
            self,
            user_id: int,
            month: Optional[int] = None,
            year: Optional[int] = None
    ) -> int:
        """Получение статистики по числу просмотров протоколов по 1 пользователю"""
        filters = []

        if month:
            filters.append(extract('month', tables.Statistics.datetime) == month)
        if year:
            filters.append(extract('year', tables.Statistics.datetime) == year)

        filters.append(tables.Reports.user_id == user_id)

        result = await self.session.execute(
            select(
                func.count(tables.Statistics.id)
            ).
            join(
                tables.Reports,
                tables.Reports.id == tables.Statistics.report_id,
                isouter=True
            ).
            filter(*filters)
        )

        return result.scalar_one()

    async def delete(self, report_id: str):
        """Удаление записи статистики по заданному отчету"""
        delete_query = delete(tables.Statistics).where(tables.Statistics.report_id == report_id)
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)
        await self.session.commit()

    async def create(self, client_ip: str, report_id: str):
        """Создание записи по статистике"""
        new_statistic = tables.Statistics(
            report_id=report_id,
            client_ip=client_ip,
            datetime=datetime.datetime.now()
        )
        self.session.add(new_statistic)
        await self.session.commit()

