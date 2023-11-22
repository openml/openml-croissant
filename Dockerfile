FROM python:3.11-bookworm

RUN apt update && apt upgrade -y
RUN python -m pip install --upgrade pip

# TODO: just pip install when the pypi is up-to-date
COPY ./dependencies/croissant/python/mlcroissant /dependency/croissants
RUN python -m pip install /dependency/croissants

COPY ./python/ /python-api
RUN python -m pip install -e "/python-api[dev]"

WORKDIR /python-api/openml_croissant

EXPOSE 8000
