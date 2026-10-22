# Croissant converter

Generating Croissant metadata descriptions for OpenML datasets.

## Usage

```bash
docker run --rm openml/croissant-converter web_api --help
```

Make sure you have a .env file to give to the web_api. This is used to retrieve a hash of the
parquet file.

```bash
MINIO_ACCESS_KEY=[KEY]
MINIO_SECRET_KEY=[SECRET]
```

Example:

```bash
docker run --rm \
  -v ~/.cache/openml:/home/unprivileged-user/.cache/openml \
  openml/croissant-converter:[VERSION] web_api.py \
  --host "0.0.0.0"
```

## Build and publish
Update the version in pyproject.toml. Use the same version in the following script:

```bash
docker build -f docker/Dockerfile --tag openml/croissant-converter:[VERSION] .
docker push openml/croissant-converter:[VERSION]
```
