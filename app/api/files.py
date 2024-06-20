from fastapi import APIRouter, Depends, Response, status, UploadFile
from typing import Optional, List
import sys

from models.files import File
from models.users import User, LicenseLevel
from services.users import get_current_user
from services.depends import get_report_service, get_s3_service
from services.reports import ReportsService
from services.s3 import S3Service
from config import configs
from modules.exceptions import exception_right, exception_file_count, exception_file_size

router = APIRouter(
    prefix="/files",
    tags=['files'])

@router.post("/")
async def upload_file(
        report_id: str,
        file: UploadFile,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service),
        s3_service: S3Service = Depends(get_s3_service)
):
    """Добавление файла"""
    if user.license_level != LicenseLevel.ENTERPRISE:
        raise exception_right

    report = await service.get(report_id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right

    files_count = await service.get_files_count_by_report(report_id=report_id)

    if files_count > configs.file_count:
        raise exception_file_count

    contents = await file.read()
    if sys.getsizeof(contents) / (1024 * 1024) > configs.file_size:
        raise exception_file_size

    format = file.filename.split(".")[-1].lower()
    filename = file.filename.replace(' ', '_')

    resp = await s3_service.upload(data=contents, key=f"georeport/files/{report_id}-{filename}")

    return await service.create_file(report_id, filename)

@router.get("/", response_model=Optional[List[File]])
async def get_files(
        report_id: str,
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр отчетов по объекту"""
    return await service.get_files(report_id=report_id)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_files(
        report_id: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service),
        s3_service: S3Service = Depends(get_s3_service)
):
    """Удаление всех файлов"""
    report = await service.get(report_id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right

    files = await service.delete_files(report_id=report_id)

    for file in files:
        resp = await s3_service.delete(f"georeport/files/{report_id}-{file.filename}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)