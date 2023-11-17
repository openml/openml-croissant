FROM python:3.12-bookworm

RUN apt update && apt upgrade -y
RUN python -m pip install --upgrade pip

COPY ./dependencies/croissant/python/mlcroissant /dependency/croissants
RUN python -m pip install /dependency/croissants

COPY ./python/ /python-api
RUN python -m pip install -e "/python-api[dev]"

WORKDIR /python-api/openml_croissant

EXPOSE 8000
ENTRYPOINT ["python", "scripts/web_api.py"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
