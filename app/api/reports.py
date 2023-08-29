from fastapi import APIRouter, Depends, Response, status, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from datetime import date
from typing import Optional, List
import hashlib
import os
import sys
from services.qr_generator import gen_qr_code

from models.reports import Report, ReportCreate, ReportUpdate
from models.files import FileCreate, File, TestTypeFile, TestTypeFileCreate
from models.users import User, LicenseLevel
from services.users import get_current_user, UsersService
from services.depends import get_report_service, get_users_service
from services.reports import ReportsService
from exceptions import exception_active, exception_license, exception_limit, exception_right, exception_file_count, \
    exception_file_size

router = APIRouter(
    prefix="/reports",
    tags=['reports'])

#@router.get("/{id}", response_model=Report)
#async def get_report(id: str, service: ReportsService = Depends(get_report_service)):
    #"""Просмотр данных отчета по id"""
    #return await service.get(id)


@router.post("/")
async def create_report(
        report_data: ReportCreate,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Создание отчета"""
    if not user.active:
        raise exception_license

    count = await service.get_reports_count(user)

    if count['count'] >= user.limit:
        raise exception_limit

    id = hashlib.sha1(
        f"{report_data.object_number} {report_data.laboratory_number} {report_data.test_type} {user.id}".encode("utf-8")).hexdigest()

    try:
        check = await service.get(id)
        return await service.update(id=id, report_data=report_data)
    except HTTPException:
        return await service.create(report_id=id, user_id=user.id, report_data=report_data)


@router.post("/qr")
def create_qr(
        id: str, user:
        User = Depends(get_current_user)
):
    """Создание qr"""
    if not user.active:
        raise exception_active

    text = f"https://georeport.ru/reports/?id={id}"
    path_to_download = os.path.join("services", "digitrock_qr.png")  # Путь до фона qr кода
    file = gen_qr_code(text, path_to_download)

    return StreamingResponse(file, media_type="image/png")


@router.post("/report_and_qr")
async def create_report_and_qr(
        report_data: ReportCreate,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Создание отчета"""
    if not user.active:
        raise exception_active

    if date.today() > user.license_end_date:
        raise exception_license

    count = await service.get_reports_count(user)

    if count['count'] >= user.limit:
        raise exception_limit

    id = hashlib.sha1(
        f"{report_data.object_number} {report_data.laboratory_number} {report_data.test_type} {user.id}".encode("utf-8")).hexdigest()
    text = f"https://georeport.ru/reports/?id={id}"
    path_to_download = os.path.join("services", "digitrock_qr.png")  # Путь до фона qr кода

    try:
        check = await service.get(id)
        await service.update(id=id, report_data=report_data)
    except HTTPException:
        await service.create(report_id=id, user_id=user.id, report_data=report_data)

    file = gen_qr_code(text, path_to_download)
    return StreamingResponse(file, media_type="image/png")


@router.put("/{id}", response_model=ReportUpdate)
async def update_report(
        id: str,
        report_data: ReportUpdate,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Обновление отчета"""
    report = await service.get(id)

    if report.user_id != user.id and not user.is_superuser:
        raise exception_right

    if not user.active:
        raise exception_active

    return await service.update(id=id, report_data=report_data)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
        id: str, user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Удаление отчета"""
    report = await service.get(id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right
    await service.delete(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/objects/{object_number}", response_model=Optional[List[Report]])
async def get_object(
        object_number: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр отчетов по объекту"""
    return await service.get_object(user_id=user.id, object_number=object_number, is_superuser=user.is_superuser)


@router.get("/objects/", response_model=List)
async def get_objects(
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр всех объектов пользователя"""
    return await service.get_objects(user_id=user.id)


@router.post("/objects/{object_number}/{activate}")
async def activate_deactivate_object(
        object_number: str, active: bool,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Активация и деактивация объекта"""
    reports = await service.get_object(user_id=user.id, object_number=object_number, is_superuser=user.is_superuser)
    if reports:
        for report in reports:
            report.active = active

        await service.update_many(id=report.id, reports=reports)
    return {"massage": f"{len(reports)} reports from object {object_number} is {'activate' if active else 'deactivate'}"}


@router.get("/count")
async def count(
        service: ReportsService = Depends(get_report_service)
):
    """Число выданных протоколов"""
    return await service.count()


@router.post("/files/")
async def upload_file(
        report_id: str,
        filename: str,
        file: UploadFile,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Добавление файла"""
    if user.license_level != LicenseLevel.ENTERPRISE:
        raise exception_right

    report = await service.get(report_id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right

    files_count = await service.get_files_count_by_report(report_id=report_id)

    if files_count > 3:
        raise exception_file_count

    contents = await file.read()
    if sys.getsizeof(contents) / (1024 * 1024) > 10:
        raise exception_file_size

    format = file.filename.split(".")[-1].lower()

    return await service.create_file(report_id, f"{filename}.{format}", contents)


@router.get("/files/{report_id}", response_model=Optional[List[File]])
async def get_files(
        report_id: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр отчетов по объекту"""
    report = await service.get(report_id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right
    return await service.get_files(report_id=report_id)


@router.delete('/files/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_files(
        report_id: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Удаление всех файлов"""
    report = await service.get(report_id)
    if report.user_id != user.id and not user.is_superuser:
        raise exception_right

    await service.delete_files(report_id=report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/test_type_files/")
async def upload_test_type_file(
        test_type: str,
        filename: str,
        file: UploadFile,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Добавление файла"""

    contents = await file.read()
    if sys.getsizeof(contents) / (1024 * 1024) > 100:
        raise exception_file_size

    format = file.filename.split(".")[-1].lower()

    return await service.create_test_type_files(user.id, test_type, f"{filename}.{format}", contents)


@router.get("/test_type_files/{report_id}", response_model=Optional[List[TestTypeFile]])
async def get_test_type_files(
        report_id: str,
        service: ReportsService = Depends(get_report_service)
):
    """Просмотр отчетов по объекту"""
    report = await service.get(report_id)
    print(report)
    return await service.get_test_type_files(test_type=report.test_type, user_id=report.user_id)


@router.delete('/test_type_files/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_type_files(
        test_type: str,
        user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Удаление всех файлов"""
    await service.delete_test_type_files(test_type=test_type, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)