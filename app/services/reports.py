import os.path
import datetime
from typing import List, Optional
import humanize
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
#import redis
#import pickle

from models.reports import Report, ReportCreate, ReportUpdate
from services.qr_generator import gen_qr_code
import db.tables as tables

_t = humanize.i18n.activate("ru_RU")

#rds = redis.Redis()

class ReportsService:
    def __init__(self, session: Session):
        self.session = session

    async def _get(self, id: str) -> Optional[tables.Reports]:
        report = await self.session.execute(
            select(tables.Reports).
            filter_by(id=id)
        )
        report = report.scalars().first()

        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return report

    async def get(self, id: str) -> tables.Reports:
        #report = rds.get(id)
        #if report:
            #return pickle.loads(report)

        report = await self._get(id)
        return report

    async def get_all(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None,
                      object_number: Optional[str] = None) -> dict:
        if object_number:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(user_id=user_id).
                filter_by(object_number=object_number).
                order_by(tables.Reports.datetime.desc()).
                offset(offset).
                limit(limit)
            )
        else:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(user_id=user_id).
                order_by(tables.Reports.datetime.desc()).
                offset(offset).
                limit(limit)
            )

        reports = reports.scalars().all()
        res = {}

        for report in reports:
            res[report.id] = {
                "datetime": humanize.naturaltime(report.datetime),
                "object_number": report.object_number,
                "laboratory_number": report.laboratory_number,
                "test_type": report.test_type,
                "data": report.data
            }
        return res

    async def get_count_in_object(self, user_id: str, object_number: Optional[str] = None) -> int:
        if object_number:
            reports = await self.session.execute(
                select(func.count(tables.Reports.id))
                .filter_by(user_id=user_id)
                .filter_by(object_number=object_number)
            )
        else:
            reports = await self.session.execute(
                select(func.count(tables.Reports.id))
                .filter_by(user_id=user_id)
            )
        count = reports.scalar_one()

        return count

    async def get_objects(self, user_id, limit: Optional[int] = None, offset: Optional[int] = None) -> list:
        reports = await self.session.execute(
            select(tables.Reports).
            filter_by(user_id=user_id).
            offset(offset).
            limit(limit)
        )
        reports = reports.scalars().all()

        objects = []

        for report in reports:
            if report.object_number not in objects:
                objects.append(report.object_number)

        if not limit or not (offset + limit < len(reports)):
            return objects[offset:len(reports)], len(objects)
        else:
            return objects[offset:offset + limit], len(objects)

    async def get_object(self, user_id: str, object_number: str, is_superuser: bool = False) -> List[tables.Reports]:
        if is_superuser:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(object_number=object_number)
            )
        else:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(user_id=user_id).
                filter_by(object_number=object_number)
            )

        reports = reports.scalars().all()

        return reports

    async def get_reports_count(self, user) -> dict:
        license_update_datetime = datetime.datetime(
            year=user.license_update_date.year,
            month=user.license_update_date.month,
            day=user.license_update_date.day
        )

        reports = await self.session.execute(
            select(func.count(tables.Reports.id))
            .filter_by(user_id=user.id)
            .filter(tables.Reports.datetime >= license_update_datetime)
        )
        count = reports.scalar_one()

        return {"count": count}

    async def update(self, id: str, report_data: ReportUpdate) -> ReportUpdate:

        report = await self.session.execute(
            select(tables.Reports)
            .filter_by(id=id)
        )

        report = report.scalars().first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No this report id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        q = update(tables.Reports).where(tables.Reports.id == id).values(
            datetime=datetime.datetime.now(),
            data=report_data.data,
            active=report_data.active
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return ReportUpdate(
            datetime=datetime.datetime.now(),
            **report_data.dict()
        )

    async def delete(self, id: str):
        q = delete(tables.Reports).where(tables.Reports.id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

    async def create(self, user_id: str, report_id: str, report_data: ReportCreate) -> tables.Reports:
        report = tables.Reports(
            **report_data.dict(),
            id=report_id,
            datetime=datetime.datetime.now(),
            user_id=user_id)
        self.session.add(report)
        await self.session.commit()

        #rds.set(report_id, pickle.dumps(report, protocol=pickle.HIGHEST_PROTOCOL))
        #rds.expire(report_id, 20*60)

        return report

    async def create_qr(self, user_id: str, laboratory_number: str, test_type: str,
                     report_data: ReportCreate):

        report = await self.create(user_id, laboratory_number, test_type, report_data)

        text = f"https://georeport.ru/report/?id={report.id}"

        path_to_download = os.path.join("static/images", "digitrock_qr.png")  # Путь до фона qr кода

        return gen_qr_code(text, path_to_download)

