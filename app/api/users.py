from fastapi import APIRouter, Depends, status, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from models.users import UserCreate, Token, User, UserUpdate, LicenseUpdate
from services.users import UsersService, get_current_user
from services.depends import get_report_service
from services.reports import ReportsService
from fastapi.security import OAuth2PasswordRequestForm
from services.depends import get_users_service

router = APIRouter(
    prefix='/authorization',
    tags=['authorization'],
)


@router.get('/', response_model=List[User])
async def get_all(
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Просмотр всех пользователей"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.get_all()


@router.post('/', response_model=User)
async def sign_up(
        user_data: UserCreate,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Регисртрация нового пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.register_new_user(user_data)


@router.post('/sign-in/')
async def sign_in(
        auth_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: UsersService = Depends(get_users_service)
):
    """Получение токена (токен зранится в куки)"""
    token = await auth_service.authenticate_user(auth_data.username, auth_data.password)
    content = {"message": "True"}
    response = JSONResponse(content=content)
    response.set_cookie("Authorization", value=f"Bearer {token.access_token}", httponly=True)
    return response


@router.get('/user/', response_model=User)
async def get_user(
        user: User = Depends(get_current_user)
):
    """Просмотр авторизованного пользователя"""
    return user


@router.get("/sign-out/")
async def sign_out_and_remove_cookie(
        current_user: User = Depends(get_current_user)
):
    content = {"message": "Tocken closed"}
    response = JSONResponse(content=content)
    response.delete_cookie("Authorization")
    return response

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        id: int,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Удаление пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await auth_service.delete(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/')
async def update_user(
        id: int, user_data: UserUpdate,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Обновление данных пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.update(id=id, user_data=user_data)


@router.get('/report_counts')
async def get_counts(
        month: int,
        year: int,
        auth_service: UsersService = Depends(get_users_service),
        service: ReportsService = Depends(get_report_service),
        current_user: User = Depends(get_current_user)
):
    """Получение количества всех выданных протоколов по пользователям"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights",
            headers={"WWW-Authenticate": "Bearer"},
        )
    users = await auth_service.get_all()
    reports_data = {}
    for user in users:
        data = await service.get_mounth_count(user.id, year, month)
        data["limit"] = user.limit
        reports_data[user.id] = data
    return reports_data


@router.put("/license", response_model=LicenseUpdate)
async def update_license(
        user_id: int,
        license_data: LicenseUpdate,
        user: User = Depends(get_current_user),
        service: UsersService = Depends(get_users_service)
):
    """Обновление лицензии"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have rights to chenge this",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.update_license(user_id=user_id, license_data=license_data)

