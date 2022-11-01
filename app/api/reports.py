from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from datetime import date, datetime
from typing import Optional, List
import hashlib
import os
from services.qr_generator import gen_qr_code

from models.reports import Report, ReportCreate, ReportUpdate
from models.users import User
from services.users import get_current_user
from services.depends import get_report_service, get_users_service
from services.reports import ReportsService
from services.users import UsersService

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if date.today() > user.license_end_date:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The license is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    count = await service.get_reports_count(user)

    if count >= user.limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Year limit reached",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if date.today() > user.license_end_date:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The license is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    id = hashlib.sha1(
        f"{report_data.object_number} {report_data.laboratory_number} {report_data.test_type} {user.id}".encode("utf-8")).hexdigest()

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have the right to do this"
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.update(id=id, report_data=report_data)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
        id: str, user: User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service)
):
    """Удаление отчета"""
    report = await service.get(id)
    if report.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have the right to do this"
        )
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
