from fastapi import APIRouter, Depends, Response, status, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import date
from typing import Optional, List
import hashlib
import os
from fastapi_cache.decorator import cache
from fastapi.concurrency import run_in_threadpool
import concurrent
import functools
import asyncio

from services.qr_generator import gen_qr_code
from models.reports import Report, ReportCreate, ReportUpdate
from models.users import User
from services.users import get_current_user
from services.depends import get_report_service
from services.depends import get_statistics_service
from services.reports import ReportsService
from services.statistics import StatisticsService
from modules.exceptions import exception_active, exception_license, exception_limit, exception_right

router = APIRouter(
    prefix="/reports",
    tags=['reports'])

@router.get("/get/", response_model=Report)
@cache(expire=60)
async def get_report(
        id: str,
        request: Request,
        service: ReportsService = Depends(get_report_service),
        stat_service: StatisticsService = Depends(get_statistics_service),
):
    """Просмотр данных отчета по id"""
    report = await service.get(id)

    if id != '4c795fb5002852b5af5df9e5de1e44b11b920d6f':
        await stat_service.create(client_ip=request.headers.get("X-Real-IP") or request.client.host, report_id=id)

    return report



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
        f"{report_data.object_number} {report_data.laboratory_number} {report_data.test_type} {user.id}".encode("utf-8")
    ).hexdigest()

    return await service.create(report_id=id, user_id=user.id, report_data=report_data)

@router.post("/qr/")
async def create_qr(
        id: str, user:
        User = Depends(get_current_user),
        service: ReportsService = Depends(get_report_service),
        stat_service: ReportsService = Depends(get_statistics_service),
):
    """Создание qr"""
    if not user.active:
        raise exception_active

    file = await service.create_qr(id)

    return StreamingResponse(file, media_type="image/png")

@router.post("/report_and_qr/")
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

    file = await service.create_qr(id)

    return StreamingResponse(file, media_type="image/png")

@router.put("/", response_model=ReportUpdate)
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

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
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

@router.get("/objects/{object_number}/", response_model=Optional[List[Report]])
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

@router.post("/objects/{object_number}/{activate}/")
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

@router.get("/count/")
@cache(expire=60)
async def count(
        service: ReportsService = Depends(get_report_service)
):
    """Число выданных протоколов"""
    return await service.count()



