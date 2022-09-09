#import requests
import datetime

data = {
    "object_number": "111-11",
    "laboratory_number": "A1-11",
    "test_type": "Резонансная колонка",
    "data": {
        "Дата выдачи протокола": datetime.datetime.now().strftime('%d.%m.%Y')
    },
    "active": True
}

def request_qr(data):
    def request_qr():
        with requests.Session() as sess:
            reg = sess.post('https://georeport.ru/authorization/sign-in/',
                            data={
                                "username": "mdgt_admin",
                                "password": "mdgt_admin_password",
                                "grant_type": "password",
                                "scope": "",
                                "client_id": "",
                                "client_secret": ""
                            }, verify=False, allow_redirects=False)

            response = sess.post('https://georeport.ru/reports/report_and_qr', json=data)
            if not response.ok:
                return (False, "Ошибка")

            with open("qr.png", "wb") as file:
                file.write(response.content)
            return (True, "")