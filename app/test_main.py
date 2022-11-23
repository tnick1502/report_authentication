from fastapi.testclient import TestClient
import requests
import datetime
#import urllib3
data = {
        "object_number": "111-11",
        "laboratory_number": "A1-11",
        "test_type": "Резонансная колонка",
        "data": {
            "Дата выдачи протокола": datetime.datetime.now().strftime('%d.%m.%Y')
        },
        "active": True
    }

from main import app

client = TestClient(app)


def test_auth():
    response = client.post(
        'authorization/sign-in/',
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

    assert response.json() == {"detail": 'Incorrect username or password'}

