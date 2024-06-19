import datetime
from typing import List, Optional
from sqlalchemy.sql import extract
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.orm import Session

import db.tables as tables
from exceptions import exception_not_found


class StatisticsService:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_report_id(self, report_id: str) -> List[tables.Statistics]:
        res = await self.session.execute(
            select(tables.Statistics).
            filter_by(report_id=report_id)
        )
        res = res.scalars().all()

        if not res:
            raise exception_not_found
        return res

    async def get_by_date(self, user_id: int, month: Optional[int] = None, year: Optional[int] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[tables.Statistics]:
        filters = []

        if month:
            filters.append(extract('month', tables.Statistics.datetime) == month)
        if year:
            filters.append(extract('year', tables.Statistics.datetime) == year)

        filters.append(tables.Reports.user_id == user_id)

        res = await self.session.execute(
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

        res = res.scalars().all()

        return res

    async def count(self, user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> int:
        filters = []

        if month:
            filters.append(extract('month', tables.Statistics.datetime) == month)
        if year:
            filters.append(extract('year', tables.Statistics.datetime) == year)

        filters.append(tables.Reports.user_id == user_id)

        res = await self.session.execute(
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
        count = res.scalar_one()

        return count

    async def delete(self, id: str):
        q_s = delete(tables.Statistics).where(tables.Statistics.report_id == id)
        q_s.execution_options(synchronize_session="fetch")
        await self.session.execute(q_s)
        await self.session.commit()

    async def create(self, client_ip: str, report_id: str):
        data = tables.Statistics(
            report_id=report_id,
            client_ip=client_ip,
            datetime=datetime.datetime.now()
        )
        self.session.add(data)
        await self.session.commit()


