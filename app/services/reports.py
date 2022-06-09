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

from models.reports import Report, ReportCreate, ReportUpdate
from services.qr_generator import gen_qr_code
import db.tables as tables

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
        report = await self._get(id)
        return report

    async def get_objects(self, user_id) -> tables.Reports:
        reports = await self.session.execute(
            select(tables.Reports).
            filter_by(user_id=user_id)
        )
        reports = reports.scalars().all()

        objects = []

        for report in reports:
            if report.object_number not in objects:
                objects.append(report.object_number)

        return objects

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
        return report

    async def create_qr(self, user_id: str, laboratory_number: str, test_type: str,
                     report_data: ReportCreate):

        report = await self.create(user_id, laboratory_number, test_type, report_data)

        text = f"https://georeport.ru/report/?id={report.id}"

        path_to_download = os.path.join("static/images", "digitrock_qr.png")  # Путь до фона qr кода

        return gen_qr_code(text, path_to_download)

