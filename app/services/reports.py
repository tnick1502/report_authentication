import os.path
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

    async def get_object(self, user_id: str, object_number: str, limit: int, skip: int) -> List[tables.Reports]:
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
            "user_id": user_id,
            "year": year,
            "month": month,
            "count": len(reports)
        }

    async def update(self, id: str, report_data: ReportUpdate) -> tables.Reports:
        q = update(tables.Reports).where(tables.Reports.id == id).values(date=report_data.date,
                                                                         object_number=report_data.object_number,
                                                                         data=report_data.data)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

    async def delete(self, date: date):
        q = delete(tables.Reports).where(tables.Reports.id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

    async def create(self, user_id: str, laboratory_number: str, test_type: str, report_data: ReportCreate) -> tables.Reports:

        id = hash(f"{report_data.object_number} {laboratory_number} {test_type} {user_id}")

        try:
            await self._get(id)
        except HTTPException:
            report = tables.Reports(
                **report_data.dict(),
                id=id,
                user_id=user_id)
            self.session.add(report)
            await self.session.flush()
            return report
        else:
            return await self.update(id, report_data)

    async def create_qr(self, user_id: str, laboratory_number: str, test_type: str,
                     report_data: ReportCreate):

        report = await self.create(user_id, laboratory_number, test_type, report_data)

        text = f"https://georeport.ru/report/?id={report.id}"

        path_to_download = os.path.join("static/images", "digitrock_qr.png")  # Путь до фона qr кода

        return gen_qr_code(text, path_to_download)




