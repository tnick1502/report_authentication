import uvicorn
from config import configs
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import http.client

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


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "template_report_link": ' http://0.0.0.0:8555/reports/'
        }
    )

@app.get("/login", response_class=HTMLResponse)
async def index(request: Request):

    return templates.TemplateResponse(
        "login.html",
        context={
            "request": request,
        }
    )

@app.get("/reports/", response_class=HTMLResponse)
async def show_report(request: Request):
    """Просмотр данных отчета по id"""
    context = {
        "request": request,
        "title": "МОСТДОРГЕОТРЕСТ",
        "link": {'link': "https://mdgt.ru/",
                 'name': "mdgt.ru"},
        "res": {
            "Значение 1": 1,
            "Значение 2": 2,
            "Значение 4": 3,
        }
    }

    return templates.TemplateResponse("show_report.html", context=context)


if __name__ == "__main__":


    uvicorn.run(
        app,
        host=configs.server_host,
        port=configs.server_port,
    )