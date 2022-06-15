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
from services.depends import get_report_service
from services.reports import ReportsService
from pathlib import Path

from db.database import async_session
from db import tables
from db.database import Base, engine
from api import router


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
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/{id}", response_class=HTMLResponse)
async def show_report(id: str, request: Request, service: ReportsService = Depends(get_report_service)):
    """Просмотр данных отчета по id"""
    data = await service.get(id)

    data = data.__dict__

    context = {
        "request": request,
        "title": 'МОСТДОГЕОТРЕСТ',
        "link": {'link': 'https://mdgt.ru', 'name': 'mdgt.ru'},
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
                        with open("superuser.json") as file:
                            superuser_data = json.load(file)

                        user = tables.Users(
                            username=superuser_data["username"],
                            password_hash=bcrypt.hash(superuser_data["password_hash"]),
                            mail=superuser_data["mail"],
                            organization=superuser_data["organization"],
                            organization_url=superuser_data["organization_url"],
                            phone=superuser_data["phone"],
                            limit=superuser_data["limit"],
                            is_superuser=superuser_data["is_superuser"],
                            active=superuser_data["active"]
                        )

                        session.add(user)

                        with open("superreport.json") as file:
                            superreport_data = json.load(file)

                        report = tables.Reports(
                            id=superreport_data["id"],
                            user_id=superreport_data["user_id"],
                            date=datetime.datetime.strptime(superreport_data["date"], '%Y-%m-%d').date(),
                            object_number=superreport_data["object_number"],
                            data=superreport_data["data"],
                            active=superreport_data["active"],
                        )
                        session.add(report)
                        await session.commit()
                    except Exception as err:
                        print("Ошибка создания суперпользователя ", str(err))
    await create_surer()



