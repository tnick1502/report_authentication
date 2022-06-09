from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.database import async_session
from db import tables
from passlib.hash import bcrypt
from sqlalchemy.future import select
import json

from db.database import Base, engine
from api import router

app = FastAPI(
    title="Georeport MDGT",
    description="Сервис аутентификации протоколов испытаний",
    version="1.0.0")


origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(router)

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
                        await session.commit()
                    except Exception as err:
                        print("Ошибка создания суперпользователя ", str(err))
    await create_surer()



