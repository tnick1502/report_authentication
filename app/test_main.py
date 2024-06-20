from fastapi.testclient import TestClient
import requests
import datetime

from main import app

client = TestClient(app)

data = {
        "object_number": "111-11",
        "laboratory_number": "A1-11",
        "test_type": "Резонансная колонка",
        "data": {
            "Дата выдачи протокола": datetime.datetime.now().strftime('%d.%m.%Y')
        },
        "active": True
    }

def main_page():
    response = client.get("/")

    assert response.status_code == 200, 'Main page error'

    '''response = client.post(
        "auth/sign-in/",
        data={
            "username": "ytv",
            "password": "lijuh",
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        },
        verify=False, allow_redirects=False
    )

    assert response.status_code == 401, "Authorization error"'''
