from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine


app = FastAPI(
    title="DashBoard MDGT",
    description="Отображение показателей работы компании",
    version="1.0.0")


origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://192.168.0.41:3000/"
    "localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
