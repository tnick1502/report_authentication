import os.path
import datetime
from typing import List, Optional
import asyncio
import concurrent
import humanize
import functools
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.sql.expression import func as expression_func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
#import redis
#import pickle

from models.reports import Report, ReportCreate, ReportUpdate
from services.qr_generator import gen_qr_code
import db.tables as tables
from modules.exceptions import exception_not_found

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
            raise exception_not_found
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

    async def count(self) -> int:
        reports = await self.session.execute(
            select(func.count(tables.Reports.id))
        )
        count = reports.scalar_one()

        return count

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
        objects = await self.session.execute(
            select(tables.Reports.object_number).
            filter_by(user_id=user_id).
            group_by(tables.Reports.object_number).
            order_by(expression_func.max(tables.Reports.datetime)).
            offset(offset).
            limit(limit)
        )
        objects = objects.scalars().all()

        return objects[::-1]

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
            raise exception_not_found

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

    async def create(self, user_id: int, report_id: str, report_data: ReportCreate) -> tables.Reports:
        #report = tables.Reports(
            #**report_data.dict(),
            #id=report_id,
            #datetime=datetime.datetime.now(),
            #user_id=user_id)
        #self.session.add(report)

        stmt = insert(tables.Reports).values(
            **report_data.dict(),
            id=report_id,
            datetime=datetime.datetime.now(),
            user_id=user_id)

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=stmt.excluded
        )
        await self.session.execute(stmt)
        await self.session.commit()

        #rds.set(report_id, pickle.dumps(report, protocol=pickle.HIGHEST_PROTOCOL))
        #rds.expire(report_id, 20*60)

        return tables.Reports(
            **report_data.dict(),
            id=report_id,
            datetime=datetime.datetime.now(),
            user_id=user_id)

    async def create_qr(self, id: str):

        text = f"https://georeport.ru/reports/?id={id}"
        path_to_download = os.path.join("services", "digitrock_qr.png")  # Путь до фона qr кода

        loop = asyncio.get_event_loop()
        with concurrent.futures.ProcessPoolExecutor() as pool:
            return await loop.run_in_executor(pool, functools.partial(gen_qr_code, text, path_to_download))

    async def get_files(self, report_id: str) -> Optional[tables.Files]:
        files = await self.session.execute(
            select(tables.Files).
                filter_by(report_id=report_id)
        )
        files = files.scalars().all()

        if not files:
            raise exception_not_found

        return files

    async def create_file(self, report_id: str, filename: str) -> tables.Files:
        file = tables.Files(
            link=f"georeport/files/{report_id}-{filename}",
            report_id=report_id,
            filename=filename
        )
        self.session.add(file)
        await self.session.commit()

        return file

    async def get_files_count_by_report(self, report_id: str) -> int:
        reports = await self.session.execute(
            select(func.count(tables.Files.id)).filter_by(report_id=report_id)
        )
        count = reports.scalar_one()

        return count

    async def delete_files(self, report_id: str):
        files = await self.session.execute(
            select(tables.Files).
                filter_by(report_id=report_id)
        )
        files = files.scalars().all()

        if not files:
            return

        q = delete(tables.Files).where(tables.Files.report_id == report_id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return files

    async def delete_file(self, file_id: int):
        q = delete(tables.Files).where(tables.Files.report_id == file_id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

    async def get_test_type_files(self, test_type: str, user_id: int) -> Optional[tables.TestTypeFiles]:
        test_type = test_type.replace(' ', '_')
        files = await self.session.execute(
            select(tables.TestTypeFiles).
                filter_by(
                test_type=test_type,
                user_id=user_id
            )
        )
        files = files.scalars().all()

        if not files:
            raise exception_not_found

        return files

    async def create_test_type_files(self, user_id: int, test_type: str, filename: str) -> tables.TestTypeFiles:
        file = tables.TestTypeFiles(
            link=f"georeport/test_type_files/{user_id}-{test_type}-{filename}",
            test_type=test_type,
            user_id=user_id,
            filename=filename
        )
        self.session.add(file)
        await self.session.commit()

        return file

    async def delete_test_type_files(self, test_type: str, user_id: int):
        test_type = test_type.replace(' ', '_')
        files = await self.session.execute(
            select(tables.TestTypeFiles).
                filter_by(
                test_type=test_type,
                user_id=user_id
            )
        )
        files = files.scalars().all()

        if not files:
            return

        q = delete(tables.TestTypeFiles).where(
            tables.TestTypeFiles.test_type == test_type,
            tables.TestTypeFiles.user_id == user_id,
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

        return files

