# croissant converter

## Usage

```bash
docker run --rm openml/croissant-converter generate_croissants.py --help
docker run --rm openml/croissant-converter upload_datasets_to_minio.py --help
```

Make sure you have a .env file to give to the uploader:
```bash
MINIO_ACCESS_KEY=[KEY]
MINIO_SECRET_KEY=[SECRET]
```

Example:

```bash
docker run --rm \
  -v ./data:/output \
  -v ~/.cache/openml:/home/unprivileged-user/.cache/openml \
  openml/croissant-converter:[VERSION] generate_croissants.py \
  --all \
  -o /output

docker run --rm \
  -v ./data:/input \
  --env-file .env \
  openml/croissant-converter:[VERSION] upload_datasets_to_minio.py \
  -i /input
```

## Build and publish
Update the version in pyproject.toml. Use the same version in the following script:

```bash
docker build -f docker/Dockerfile --tag openml/croissant-converter:[VERSION] .
docker push openml/croissant-converter:[VERSION]
```
