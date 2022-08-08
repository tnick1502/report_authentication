from fastapi import APIRouter, Depends, Response, status, HTTPException

from models.license import LicenseCreate, LicenseUpdate, License
from models.users import User
from services.users import get_current_user
from services.license import LicensesService
from services.depends import get_licenses_service


router = APIRouter(
    prefix="/license",
    tags=['license']
)


@router.get("/", response_model=License)
async def get_license(
        user: User = Depends(get_current_user),
        service: LicensesService = Depends(get_licenses_service)
):
    """Получение лицензии пользователя"""
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.get(user_id=user.id)


@router.post("/", response_model=License)
async def create_license(
        license_data: LicenseCreate,
        user: User = Depends(get_current_user),
        service: LicensesService = Depends(get_licenses_service)
):
    """Создание лицензии"""
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.create(user=user, license_data=license_data)


@router.put("/{id}", response_model=LicenseUpdate)
async def update_license(
        user_id: int,
        license_data: LicenseUpdate,
        user: User = Depends(get_current_user),
        license_service: LicensesService = Depends(get_licenses_service)
):
    """Обновление лицензии"""
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights to chenge this",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await license_service.update(user_id=user_id, license_data=license_data)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_license(
        user_id: str,
        user: User = Depends(get_current_user),
        license_service: LicensesService = Depends(get_licenses_service)
):
    """Удаление лицензии"""
    await license_service.get(user_id)

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights to chenge this certificate",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await license_service.delete(user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/licenses')
async def get_license(
        user: User = Depends(get_current_user),
        license_service: LicensesService = Depends(get_licenses_service)
):
    """Получение всех лицензий"""

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await license_service.get_all()

