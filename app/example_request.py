#import requests

def request_qr():
    with requests.Session() as sess:
        reg = sess.post('http://0.0.0.0:9000/authorization/sign-in/',
                        data={
                            "username": "mdgt_admin",
                            "password": "mdgt_admin",
                            "grant_type": "password",
                            "scope": "",
                            "client_id": "",
                            "client_secret": ""
                        }, verify=False, allow_redirects=False)

        response = sess.post('http://0.0.0.0:9000/reports/qr?id=2e7a1c2a70da23e400e776cab7189d02c4cfd33b')
        assert response.ok, "Не удалось сгенерировать код"
        with open("qr.png", "wb") as file:
            file.write(response.content)
        return "qr.png"