# Georeport

### Сервис для аутентификации протоколов лабораторных испытаний. 

#### Функционал:
* сервис данных пользователей
* сервис лицензий хранит данные лицензий и проверяет лицензию пользователя при отправке запросов пользователя
* сервис отчетов хранит данные по всем отчетам в базе

#### Стек:
* fastapi
* postgresql

#### [Схема БД](https://dbdiagram.io/d/63088a2bf1a9b01b0feae726)

## Запуск:
1. Скопировать файл .env в корень проекта
    
2. Создать папку для проекта. Открыть папку в терминале и выполнить:\
    `git init`\
    `git clone https://github.com/tnick1502/report_authentication.git`

3. Запуск через docker-compose\
    `docker-compose up`

