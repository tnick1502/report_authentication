import requests

response = requests.post(
        'http://georeport.ru/authorization/sign-in/',
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
print(response.status_code)
assert False, "efv"
#assert response.json() == {"detail": 'Incorrect username or password'}