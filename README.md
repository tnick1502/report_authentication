# Georeport

### Сервис для аутентификации протоколов лабораторных испытаний. 

#### Функционал:
* сервис данных пользователей
* сервис лицензий хранит данные лицензий и проверяет лицензию пользователя при отправке запросов пользователя
* сервис отчетов хранит данные по всем отчетам в базе

#### Стек:
* fastapi + postgresql + sqlalchemy
* html + CSS + js

#### [Схема БД](https://dbdiagram.io/d/64edcb6a02bd1c4a5e99ec69)

## Для разработки:
1. Скопировать файл .env в корень проекта
    
2. Создать папку для проекта. Открыть папку в терминале и выполнить:\
    `git init`\
    `git clone https://github.com/tnick1502/report_authentication.git`

3. Запуск через docker-compose:\
    `docker-compose -f docker-compose-dev.yml up`\
	или моя Mac:\
    `docker-compose -f docker-compose-dev-mac.yml --env-file ./env.txt up`

## Деплой:
~/ = папка проекта 

1. Скопировать файл .env в ~/

2. Добавить конфигуратор nginx. Дефолтный конфигуратор nginx находится в ~/server/conf.d/app.conf (устанавливается автоматически в докер). Сертификат и ключ key.key и crt.crt должны находится в папке ~/*
    
3. Открыть папку ~/ в терминале и выполнить:\
    `git init`\
    `git clone https://github.com/tnick1502/report_authentication.git`

4. Запуск через docker-compose:\
    `docker-compose up --force-recreate -d --build`


Для очищения докера от проекта:\
    `docker rm $(docker ps -a -q) -f`\
    `docker rmi $(docker images -a -q) -f`

