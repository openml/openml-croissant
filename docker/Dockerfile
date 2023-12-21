FROM python:3.11-slim-bookworm

RUN apt update && apt upgrade -y
RUN python -m pip install --upgrade pip

COPY ./python/ /app
RUN python -m pip install -e "/app[dev]"


RUN useradd --create-home unprivileged-user
USER unprivileged-user

WORKDIR /app/openml_croissant/scripts

ENTRYPOINT ["python3"]
