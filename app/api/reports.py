from fastapi import APIRouter, Depends, Response, status

from models.reports import Report, ReportCreate
from models.users import User
from services.users import get_current_user
from services.reports import ReportsService
from services.depends import get_report_service

router = APIRouter(
    prefix="/reports",
    tags=['reports'])


@router.get("/{id}", response_model=Report)
async def get_report(id: str, service: ReportsService = Depends(get_report_service)):
    return await service.get(id)


@router.post("/", response_model=Report)
async def create_report(laboratory_number: str, test_type: str, report_data: ReportCreate,
                        user: User = Depends(get_current_user), service: ReportsService = Depends(get_report_service)):
    return await service.create(user_id=user.id, laboratory_number=laboratory_number, test_type=test_type, report_data=report_data)


@router.delete('/{date}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(id: str, user: User = Depends(get_current_user), service: ReportsService = Depends(get_report_service)):
    await service.delete(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


