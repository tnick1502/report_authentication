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

from models.reports import Report, ReportCreate, ReportUpdate
from services.qr_generator import gen_qr_code
import db.tables as tables
from modules.exceptions import exception_not_found

# Активация локализации для humanize
_t = humanize.i18n.activate("ru_RU")

class ReportsService:
    def __init__(self, session: Session):
        self.session = session

    async def _get(self, id: str) -> Optional[tables.Reports]:
        """Асинхронное получение отчета по ID с проверкой на существование"""
        result = await self.session.execute(
            select(tables.Reports).filter_by(id=id)
        )
        report = result.scalars().first()

        if not report:
            raise exception_not_found
        return report

    async def get(self, id: str) -> tables.Reports:
        """Асинхронное получение отчета с валидацией через _get"""
        return await self._get(id)

    async def get_all(self,
                      user_id: str,
                      limit: Optional[int] = None,
                      offset: Optional[int] = None,
                      object_number: Optional[str] = None) -> dict:
        """Асинхронное получение всех отчетов пользователя с поддержкой пагинации и фильтрации"""
        query = select(tables.Reports).filter_by(user_id=user_id)
        if object_number:
            query = query.filter_by(object_number=object_number)

        query = query.order_by(tables.Reports.datetime.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        reports = result.scalars().all()

        # Генерация результата с humanize
        return {
            report.id: {
                "datetime": humanize.naturaltime(report.datetime),
                "object_number": report.object_number,
                "laboratory_number": report.laboratory_number,
                "test_type": report.test_type,
                "data": report.data
            } for report in reports
        }

    async def count(self) -> int:
        """Асинхронное получение общего количества отчетов"""
        result = await self.session.execute(
            select(func.count(tables.Reports.id))
        )
        return result.scalar_one()

    async def get_count_in_object(self, user_id: str, object_number: Optional[str] = None) -> int:
        """Получение количества отчетов в объекте для пользователя"""
        query = select(func.count(tables.Reports.id)).filter_by(user_id=user_id)
        if object_number:
            query = query.filter_by(object_number=object_number)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_objects(self, user_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> list:
        """Асинхронное получение списка объектов пользователя, отсортированных по дате"""
        result = await self.session.execute(
            select(tables.Reports.object_number)
            .filter_by(user_id=user_id)
            .group_by(tables.Reports.object_number)
            .order_by(func.max(tables.Reports.datetime).desc())
            .offset(offset).limit(limit)
        )
        objects = result.scalars().all()

        return objects[::-1]

    async def get_object(self, user_id: str, object_number: str, is_superuser: bool = False) -> List[tables.Reports]:
        """Асинхронное получение списка отчетов по объекту"""
        query = select(tables.Reports).filter_by(object_number=object_number)

        if not is_superuser:
            query = query.filter_by(user_id=user_id)

        result = await self.session.execute(query)
        reports = result.scalars().all()

        return reports

    async def get_reports_count(self, user) -> dict:
        """Получение количества отчетов после обновления лицензии пользователя"""
        license_update_datetime = datetime.datetime(
            year=user.license_update_date.year,
            month=user.license_update_date.month,
            day=user.license_update_date.day
        )

        result = await self.session.execute(
            select(func.count(tables.Reports.id))
            .filter_by(user_id=user.id)
            .filter(tables.Reports.datetime >= license_update_datetime)
        )
        count = result.scalar_one()

        return {"count": count}

    async def update(self, id: str, report_data: ReportUpdate) -> ReportUpdate:
        """Обновление отчета по ID"""
        result = await self.session.execute(
            select(tables.Reports).filter_by(id=id)
        )

        report = result.scalars().first()

        if not report:
            raise exception_not_found  # Исключение, если отчет не найден

        query = update(tables.Reports).where(tables.Reports.id == id).values(
            datetime=datetime.datetime.now(),
            data=report_data.data,
            active=report_data.active
        )
        query.execution_options(synchronize_session="fetch")
        await self.session.execute(query)

        return ReportUpdate(
            datetime=datetime.datetime.now(),
            **report_data.dict()
        )

    async def delete(self, id: str):
        """Удаление отчета по ID и связанных данных"""
        q = delete(tables.Reports).where(tables.Reports.id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

    async def create(self, user_id: int, report_id: str, report_data: ReportCreate) -> tables.Reports:
        """Создание нового отчета"""
        update_query = insert(tables.Reports).values(
            **report_data.dict(),
            id=report_id,
            datetime=datetime.datetime.now(),
            user_id=user_id)

        # Обновление, если отчет с таким ID уже существует
        update_query = update_query.on_conflict_do_update(
            index_elements=['id'],
            set_=update_query.excluded
        )
        await self.session.execute(update_query)

        return tables.Reports(
            **report_data.dict(),
            id=report_id,
            datetime=datetime.datetime.now(),
            user_id=user_id)

    async def create_qr(self, id: str):
        """Создание QR-кода для отчета"""
        text = f"https://georeport.ru/reports/?id={id}"
        path_to_download = os.path.join("services", "digitrock_qr.png")  # Путь до фона qr кода

        loop = asyncio.get_event_loop()
        with concurrent.futures.ProcessPoolExecutor() as pool:
            return await loop.run_in_executor(pool, functools.partial(gen_qr_code, text, path_to_download))

    async def get_files(self, report_id: str) -> Optional[tables.Files]:
        """Получение файлов по ID отчета"""
        result = await self.session.execute(
            select(tables.Files).filter_by(report_id=report_id)
        )
        files = result.scalars().all()

        if not files:
            raise exception_not_found  # Исключение, если файлы не найдены

        return files

    async def create_file(self, report_id: str, filename: str) -> tables.Files:
        """Создание файла для отчета"""
        file = tables.Files(
            link=f"georeport/files/{report_id}-{filename}",
            report_id=report_id,
            filename=filename
        )
        self.session.add(file)

        return file

    async def get_files_count_by_report(self, report_id: str) -> int:
        """Получение количества файлов по ID отчета"""
        result = await self.session.execute(
            select(func.count(tables.Files.id)).filter_by(report_id=report_id)
        )
        count = result.scalar_one()

        return count

    async def delete_files(self, report_id: str):
        """Удаление всех файлов, связанных с отчетом"""
        result = await self.session.execute(
            select(tables.Files).filter_by(report_id=report_id)
        )
        files = result.scalars().all()

        if not files:
            return []# Если файлов нет, ничего не делаем

        delete_query = delete(tables.Files).where(tables.Files.report_id == report_id)
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)
        return files

    async def delete_file(self, file_id: int):
        """Удаление файла по ID"""
        delete_query = delete(tables.Files).where(tables.Files.id == file_id)
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)

    async def get_test_type_files(self, test_type: str, user_id: int) -> Optional[tables.TestTypeFiles]:
        """Получение файлов типов отчета"""
        test_type = test_type.replace(' ', '_')
        result = await self.session.execute(
            select(tables.TestTypeFiles).
                filter_by(
                test_type=test_type,
                user_id=user_id
            )
        )
        files = result.scalars().all()

        if not files:
            raise exception_not_found

        return files

    async def create_test_type_files(self, user_id: int, test_type: str, filename: str) -> tables.TestTypeFiles:
        """Создание файлов типов отчета"""
        file = tables.TestTypeFiles(
            link=f"georeport/test_type_files/{user_id}-{test_type}-{filename}",
            test_type=test_type,
            user_id=user_id,
            filename=filename
        )
        self.session.add(file)

        return file

    async def delete_test_type_files(self, test_type: str, user_id: int):
        """Удаление файлов типов отчета"""
        test_type = test_type.replace(' ', '_')
        result = await self.session.execute(
            select(tables.TestTypeFiles).
                filter_by(
                test_type=test_type,
                user_id=user_id
            )
        )
        files = result.scalars().all()

        if not files:
            return

        delete_query = delete(tables.TestTypeFiles).where(
            tables.TestTypeFiles.test_type == test_type,
            tables.TestTypeFiles.user_id == user_id,
        )
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)

        return files

