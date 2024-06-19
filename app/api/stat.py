from fastapi import APIRouter, Depends, Response, status, HTTPException
from typing import Optional
from fastapi_cache.decorator import cache
from services.users import get_current_user
from services.depends import get_statistics_service
from services.statistics import StatisticsService
import datetime
from dateutil.relativedelta import relativedelta

router = APIRouter(
    prefix="/stat",
    tags=['stat'])


@router.get("/count/")
@cache(expire=10)
async def count(
        month: Optional[int] = None,
        year: Optional[int] = None,
        User = Depends(get_current_user),
        service: StatisticsService = Depends(get_statistics_service),
):
    """Число просмотренных протоколов"""
    return await service.count(user_id=User.id, month=month, year=year)

@router.get("/")
@cache(expire=10)
async def get_stat(
        month: Optional[int] = None,
        year: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        User = Depends(get_current_user),
        service: StatisticsService = Depends(get_statistics_service),
):
    """Просмотр статистики за месяц"""
    return await service.get_by_date(user_id=User.id, month=month, year=year, limit=limit, offset=offset)

@router.get("/period_count")
@cache(expire=10)
async def period_count(
        User=Depends(get_current_user),
        service: StatisticsService = Depends(get_statistics_service),
):
    """Просмотр статистики за месяц"""
    res = {}
    current_date = datetime.date.today()

    # Заданная дата в прошлом
    past_date = datetime.date(2024, 5, 1)

    # Вычисление числа месяцев между датами
    months_diff = (current_date.year - past_date.year) * 12 + current_date.month - past_date.month

    for i in range(months_diff + 1):
        date = datetime.date.today() - relativedelta(months=i)
        count = await service.count(user_id=User.id, month=date.month, year=date.year)
        res[str(datetime.date(year=date.year, month=date.month, day=1))] = count

    return res



