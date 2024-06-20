FROM python:3.10

WORKDIR /code/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH=$PATH:$HOME/.poetry/bin

EXPOSE 8555

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - \
    && ln -s /etc/poetry/bin/poetry /usr/local/bin/poetry

COPY ./poetry.lock /code/poetry.lock
COPY ./pyproject.toml /code/pyproject.toml

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY ./app /code/app
COPY ./.env /code/app/.env

RUN apt-get update
RUN apt-get install -y libzbar-dev
RUN dpkg -L libzbar-dev; ls -l /usr/include/zbar.h

RUN chmod -R 777 ./


# COPY crt.crt /etc/ssl/
# COPY key.key /etc/ssl/
