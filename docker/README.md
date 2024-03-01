# croissant converter

## Usage

```bash
docker run --rm openml/croissant-converter generate_croissants.py --help
docker run --rm openml/croissant-converter upload_datasets_to_minio.py --help
```


## Build and publish

Update the version in pyproject.toml. Use the same version in the following script:

```bash
docker build -f docker/Dockerfile --tag openml/croissant-converter:[VERSION] .
docker push openml/croissant-converter:[VERSION]
```
