FROM python:3.9

WORKDIR /code/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8555

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./app /code/app
COPY ./.env /code/app/.env


RUN apt-get update
RUN apt-get install -y libzbar-dev
RUN dpkg -L libzbar-dev; ls -l /usr/include/zbar.h

RUN chmod -R 777 ./


COPY crt.crt /etc/ssl/
COPY key.key /etc/ssl/
