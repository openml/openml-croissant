FROM python:3.11-bookworm

RUN apt update && apt upgrade -y
RUN python -m pip install --upgrade pip

COPY ./python/ /python-api
RUN python -m pip install -e "/python-api[dev]"

WORKDIR /python-api/openml_croissant

EXPOSE 8000
