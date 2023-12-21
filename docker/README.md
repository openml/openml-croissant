# croissant converter

## Usage

```bash
docker run --rm openml/croissant-converter generate_croissants.py --help
docker run --rm openml/croissant-converter upload_datasets_to_minio.py --help
```


## Build and publish
```bash
docker build -f docker/Dockerfile --tag openml/croissant-converter:latest .
docker push openml/croissant-converter:latest
```
