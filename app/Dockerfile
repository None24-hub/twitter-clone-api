# Dockerfile (в корне проекта)
FROM python:3.12

RUN apt update && apt install -y postgresql-client gcc build-essential libpq-dev

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .