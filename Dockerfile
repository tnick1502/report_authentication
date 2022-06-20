cFROM python:3.9

WORKDIR /code/app

EXPOSE 8555

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./superreport.json /code/app/superreport.json
COPY ./superuser.json /code/app/superuser.json
