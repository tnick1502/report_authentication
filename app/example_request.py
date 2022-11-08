#import requests
#import datetime
#import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def request_qr(data):
    with requests.Session() as sess:
        sess.post('https://georeport.ru/authorization/sign-in/',
                  data={
                      "username": "trial",
                      "password": "trial",
                      "grant_type": "password",
                      "scope": "",
                      "client_id": "",
                      "client_secret": ""
                  },
                  verify=False, allow_redirects=False
                  )

        response = sess.post('https://georeport.ru/reports/report_and_qr', json=data)
        if not response.ok:
            return (False, response.json()['detail'])

        qr_path = f"{data['object_number']} {data['laboratory_number']} {data['test_type']}.png"

        with open(qr_path, "wb") as file:
            file.write(response.content)
        return (True, qr_path)

if __name__ == "__main__":

    data = {
        "object_number": "111-11",
        "laboratory_number": "A1-11",
        "test_type": "Резонансная колонка",
        "data": {
            "Дата выдачи протокола": datetime.datetime.now().strftime('%d.%m.%Y')
        },
        "active": True
    }

    print(request_qr(data))