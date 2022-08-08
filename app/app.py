import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from sqlalchemy.future import select
import json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import http.client

from db.database import async_session
from db import tables
from db.database import Base, engine
from api import router
from services.depends import get_report_service, get_users_service
from services.reports import ReportsService
from services.users import UsersService
from config import configs


def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

def create_ip_ports_array(ip: str, *ports):
    array = []
    for port in ports:
        array.append(f"{ip}:{str(port)}")
    return array


app = FastAPI(
    title="Georeport MDGT",
    description="Сервис аутентификации протоколов испытаний",
    version="1.0.0")


origins = [
    "http://localhost:3000",
    "http://localhost:8080"]

origins += create_ip_ports_array(get_self_public_ip(), 3000, 8000, 80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "template_report_link": 'https://georeport.ru/report/?id=95465771a6f399bf52cd57db2cf640f8624fd868'
        }
    )

@app.get("/reports/{id}", response_class=HTMLResponse)
async def show_report(id: str, request: Request,
                      service: ReportsService = Depends(get_report_service),
                      users: UsersService = Depends(get_users_service)):
    """Просмотр данных отчета по id"""
    data = await service.get(id)
    data = data.__dict__

    user_data = await users.get(data["user_id"])
    user_data = user_data.__dict__

    context = {
        "request": request,
        "title": user_data["organization"],
        "link": {'link': user_data["organization_url"],
                 'name': user_data["organization_url"][user_data["organization_url"].index("//") + 2:].replace("/",
                                                                                                               "")},
        "res": data["data"]
    }

    return templates.TemplateResponse("show_report.html", context=context)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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
                            active=True
                        )

                        session.add(user)


                        report = tables.Reports(
                            id="95465771a6f399bf52cd57db2cf640f8624fd868",
                            user_id=1,
                            date=datetime.date.today(),
                            object_number="1",
                            data={
                                "Лабораторный номер": "Э1-1/-/ТС",
                                "Объект": "-",
                                "Даты выдачи протокола": "2022-04-26",
                                "Модуль деформации E50, МПа": 11.9,
                                "Коэффициент поперечной деформации ν, д.е.:": 0.27
                            },
                            active=True,
                        )
                        session.add(report)

                        license = tables.Licenses(
                            id=1,
                            user_id=1,
                            license_level="pro",
                            license_end_date=datetime.date(year=2030, month=12, day=31),
                            license_update_date=datetime.date.today(),
                            limit=1000000000
                        )
                        session.add(license)

                        await session.commit()
                    except Exception as err:
                        print("Ошибка создания суперпользователя ", str(err))

    await create_surer()



