import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from starlette.exceptions import HTTPException as StarletteHTTPException
import humanize
import os

from db.database import async_session
from fastapi.security.utils import get_authorization_scheme_param
from services.users import get_current_user
from db import tables
from db.database import Base, engine
from api import router
from models.users import User
from services.depends import get_report_service, get_users_service
from services.reports import ReportsService
from services.users import UsersService
from config import configs
from db.tables import LicenseLevel

def create_ip_ports_array(ip: str, *ports):
    array = []
    for port in ports:
        array.append(f"{ip}:{str(port)}")
    return array


app = FastAPI(
    title="Georeport MDGT",
    description="Сервис аутентификации протоколов испытаний",
    version="1.1.0")


origins = [
    "http://localhost:3000",
    "http://localhost:8080"]

origins += create_ip_ports_array(configs.host_ip, 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


app.include_router(router)

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

#app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "template_report_link": f'https://georeport.ru/reports/?id=95465771a6f399bf52cd57db2cf640f8624fd868'
        }
    )


@app.get("/login/", response_class=HTMLResponse)
async def login(
        request: Request,
        page: Optional[int] = 1,
        object_number: Optional[str] = None,
        report_service: ReportsService = Depends(get_report_service)
):
    try:
        authorization: str = request.cookies.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if token:
            limit = 30
            user = get_current_user(token)
            count = await report_service.get_reports_count(
                user=user,
            )

            objects = await report_service.get_objects(
                user_id=user.id,
                limit=None,
                offset=0
            )
            objects_count = len(objects)

            if not object_number:
                object_number = objects[0] if objects_count else None

            reports = await report_service.get_all(
                user_id=user.id,
                limit=limit,
                offset=(page - 1) * limit,
                object_number=object_number
            )


            reports_count = await report_service.get_count_in_object(
                user_id=user.id,
                object_number=object_number
            )

            pages = int((reports_count - 1) / limit) + 1

            return templates.TemplateResponse(
                "personal.html",
                context={
                    "request": request,
                    "username": user.username,
                    "license_level": user.license_level.value,
                    "license_end_date": humanize.naturaldate(user.license_end_date),
                    "limit": user.limit,
                    "count": count["count"],
                    "reports": reports,
                    "objects": objects,
                    "pages_reports": pages,
                    "object_number": object_number
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'Authenticate': 'Bearer'},
        )

    except HTTPException:
        return templates.TemplateResponse(
            "login.html",
            context={
                "request": request,
            }
        )


@app.get("/sign-out/")
async def sign_out_and_remove_cookie(
        request: Request,
        current_user: User = Depends(get_current_user)):
    response = templates.TemplateResponse(
        "login.html",
        context={
            "request": request
        }
        )
    response.delete_cookie("Authorization")
    return response


@app.get("/reports/", response_class=HTMLResponse)
async def show_report(
        request: Request,
        id: str = '',
        service: ReportsService = Depends(get_report_service),
        users: UsersService = Depends(get_users_service)
):
    """Просмотр данных отчета по id"""
    if len(id) != 40:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong id"
        )
    data = await service.get(id)
    data = data.__dict__

    user_data = await users.get(data["user_id"])
    user_data = user_data.__dict__

    try:
       get_files = await service.get_files(id)
       files = {f.filename: f.link for f in get_files}
    except:
        files = {}

    context = {
        "request": request,
        "title": user_data["organization"],
        "link": {'link': user_data["organization_url"],
                 'name': user_data["organization_url"][user_data["organization_url"].index("//") + 2:].replace("/",
                                                                                                               "")},
        "res": {
            "Объект": data["object_number"],
            "Лабораторный номер": data["laboratory_number"],
            "Тип опыта": data["test_type"],
            **data["data"]},
        "files": files
    }

    return templates.TemplateResponse("show_report.html", context=context)


@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request: Request, exc: StarletteHTTPException):
    # print(exc.status_code, exc.detail)
    if exc.status_code == 404:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=exc.status_code)
    else:
        # Generic error page
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"{exc.detail}"},
        )


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def create_surer():
        async with async_session() as session:
            async with session.begin():

                user_names = await session.execute(
                    select(tables.Users).
                    filter_by(username="mdgt_admin")
                )
                user_names = user_names.scalars().first()

                if not user_names:

                    try:
                        user = tables.Users(
                            username=configs.superuser_name,
                            password_hash=bcrypt.hash(configs.superuser_password),
                            mail="tnick1502@mail.ru",
                            organization="МОСТДОРГЕОТРЕСТ",
                            organization_url="https://mdgt.ru/",
                            phone=74956566910,
                            is_superuser=True,
                            active=True,
                            license_level=LicenseLevel.ENTERPRISE,
                            license_end_date=datetime.date(year=2030, month=12, day=31),
                            license_update_date=datetime.date.today(),
                            limit=1000000000
                        )

                        session.add(user)

                        user_trial = tables.Users(
                            username="trial",
                            password_hash=bcrypt.hash("trial"),
                            mail="nick.mdgt@mail.ru",
                            organization="МОСТДОРГЕОТРЕСТ",
                            organization_url="https://mdgt.ru/",
                            phone=70000000000,
                            is_superuser=False,
                            active=True,
                            license_level=LicenseLevel.STANDART,
                            license_end_date=datetime.date(year=2030, month=12, day=31),
                            license_update_date=datetime.date.today(),
                            limit=100
                        )

                        session.add(user_trial)

                        report = tables.Reports(
                            id="95465771a6f399bf52cd57db2cf640f8624fd868",
                            user_id=1,
                            datetime=datetime.datetime.now(),
                            laboratory_number="1",
                            test_type="Трехосное нагружение",
                            object_number="1",
                            data={
                                "Лабораторный номер": "Э1-1/-/ТС",
                                "Объект": "-",
                                "Даты выдачи протокола": "2022-04-26",
                                "Модуль деформации E, МПа:": 8.3,
                                "Модуль деформации E50, МПа": 7.7,
                                "Коэффициент поперечной деформации ν, д.е.": 0.41,
                                "Модуль повторного нагружения Eur, МПа:": 33.6,
                            },
                            active=True,
                        )
                        session.add(report)

                        for i in range(50):

                            import random

                            E = round(random.uniform(15, 50), 2)
                            c = round(random.uniform(0.001, 0.05), 3)
                            fi = round(random.uniform(25, 35), 2)

                            report = tables.Reports(
                                id=f"9546577{i}6f399bf52cd57db2cf640f8624fd868",
                                user_id=2,
                                datetime=datetime.date.today(),
                                object_number=random.choice(["112-54", "341-15", "294-41"]),
                                laboratory_number=f"1{i}",
                                test_type="Трехосное нагружение",
                                data={
                                    "Модуль деформации E50, МПа": E,
                                    "Эффективный угол внутреннего трения, град": fi,
                                    "Эффективное сцепление c, МПа": c,
                                },
                                active=True,
                            )
                            session.add(report)

                        await session.commit()
                        print("Создан суперпользователь")
                    except Exception as err:
                        print("Ошибка создания суперпользователя ", str(err))

    await create_surer()



