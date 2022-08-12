import os.path
import hashlib
import datetime
from typing import List, Optional
from datetime import date
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
import redis
import pickle

from models.reports import Report, ReportCreate, ReportUpdate
from models.license import License
from services.qr_generator import gen_qr_code
import db.tables as tables


rds = redis.Redis()

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
        report = rds.get(id)
        if report:
            return pickle.loads(report)

        report = await self._get(id)
        return report

    async def get_all(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None,
                      object_number: Optional[str] = None) -> dict:
        if object_number:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(user_id=user_id).
                filter_by(object_number=object_number).
                order_by(tables.Reports.date).
                offset(offset).
                limit(limit)
            )
        else:
            reports = await self.session.execute(
                select(tables.Reports).
                filter_by(user_id=user_id).
                order_by(tables.Reports.date).
                offset(offset).
                limit(limit)
            )

        reports = reports.scalars().all()
        res = {}

        for report in reports:
            res[report.id] = {
                "object_number": report.object_number,
                "date": report.date,
                "data": report.data
            }
        return res

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

    async def get_reports_count(self, user_id: int, license: License) -> dict:
        reports = await self.session.execute(
            select(tables.Reports)
            .filter_by(user_id=user_id)
            .filter(tables.Reports.date >= license.license_update_date)
        )
        reports = reports.scalars().all()
        return {"count": len(reports)}

    async def get_mounth_reports(self, user_id, year: int, month: int) -> List[tables.Reports]:
        reports = await self.session.execute(
            select(tables.Reports)
            .filter_by(user_id=user_id)
            .filter(extract('year', tables.Reports.date) == year)
            .filter(extract('month', tables.Reports.date) == month)
        )
        reports = reports.scalars().all()

        return reports

    async def get_mounth_count(self, user_id, year, month) -> dict:
        reports = await self.get_mounth_reports(user_id, year, month)

        return {
            "year": year,
            "month": month,
            "count": len(reports)
        }

    async def update(self, id: str, user_id, report_data: ReportUpdate) -> Report:

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
            object_number=report_data.object_number,
            data=report_data.data,
            active=report_data.active
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return Report(
            id=id,
            user_id=user_id,
            date=datetime.date.today(),
            **report_data.dict()
        )

    async def update_many(self, id: str, reports) -> Report:

        for report in reports:
            report_data = ReportUpdate(
                object_number=report.object_number,
                data=report.data,
                active=report.active,
            )

            q = update(tables.Reports).where(tables.Reports.id == id).values(
                object_number=report_data.object_number,
                data=report_data.data,
                active=report_data.active
            )
            q.execution_options(synchronize_session="fetch")
            await self.session.execute(q)
        return await self.session.commit()


    async def delete(self, id: str):
        q = delete(tables.Reports).where(tables.Reports.id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

    async def create(self, user_id: str, report_id: str, report_data: ReportCreate) -> tables.Reports:
        report = await self.session.execute(
            select(tables.Reports)
            .filter_by(id=report_id)
        )

        report = report.scalars().first()

        if report:
            return await self.update(id=report_id, user_id=user_id, report_data=report_data)

        report = tables.Reports(
            **report_data.dict(),
            id=report_id,
            date=datetime.date.today(),
            user_id=user_id)
        self.session.add(report)
        await self.session.commit()

        rds.set(report_id, pickle.dumps(report, protocol=pickle.HIGHEST_PROTOCOL))
        rds.expire(report_id, 20*60)

        return report

    async def create_qr(self, user_id: str, laboratory_number: str, test_type: str,
                     report_data: ReportCreate):

        report = await self.create(user_id, laboratory_number, test_type, report_data)

        text = f"https://georeport.ru/report/?id={report.id}"

        path_to_download = os.path.join("static/images", "digitrock_qr.png")  # Путь до фона qr кода

        return gen_qr_code(text, path_to_download)

