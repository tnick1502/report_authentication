from fastapi import APIRouter, Depends, Response, status, UploadFile
from typing import Optional, List
import sys

from models.files import TestTypeFile, TestTypeFileCreate
from models.users import User, LicenseLevel
from services.users import get_current_user
from services.depends import get_report_service, get_s3_service
from services.reports import ReportsService
from services.s3 import S3Service
from modules.exceptions import exception_right, exception_file_count, exception_file_size

router = APIRouter(
    prefix="/test_type_files",
    tags=['test_type_files'])

@router.post("/")
async def upload_test_type_file(
        test_type: str,
        file: UploadFile,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service),
        s3_service: S3Service = Depends(get_s3_service)
):
    """Добавление файла"""

    contents = await file.read()
    if sys.getsizeof(contents) / (1024 * 1024) > 100:
        raise exception_file_size

    format = file.filename.split(".")[-1].lower()

    filename = file.filename.replace(' ', '_')
    test_type = test_type.replace(' ', '_')

    resp = await s3_service.upload(data=contents, key=f"georeport/test_type_files/{user.id}-{test_type}-{filename}")

    return await service.create_test_type_files(user.id, test_type, filename)


@router.get("/{report_id}", response_model=Optional[List[TestTypeFile]])
async def get_test_type_files(
        report_id: str,
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр отчетов по объекту"""
    report = await service.get(report_id)
    return await service.get_test_type_files(test_type=report.test_type, user_id=report.user_id)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_type_files(
        test_type: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service),
        s3_service: S3Service = Depends(get_s3_service)
):
    """Удаление всех файлов"""
    files = await service.delete_test_type_files(test_type=test_type, user_id=user.id)

    for file in files:
            resp = await s3_service.delete(f"georeport/test_type_files/{user.id}-{test_type}-{file.filename}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
