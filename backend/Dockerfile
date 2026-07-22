FROM python:3.10-slim-bookworm

WORKDIR /code/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8555

RUN apt-get -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends libzbar0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry==1.8.3

COPY poetry.lock /code/poetry.lock
COPY pyproject.toml /code/pyproject.toml

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY app /code/app

RUN chmod -R 777 ./


# COPY crt.crt /etc/ssl/
# COPY key.key /etc/ssl/
