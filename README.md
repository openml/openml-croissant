# openml-croissant 🥐
Converting dataset metadata from OpenML to [Croissant](https://github.com/mlcommons/croissant) format

## Docker

Currently, you'll have to install the `mlcroissant` dependency manually, because PYPI is not
up-to-date.

```bash
mkdir dependencies
cd dependencies
git clone https://github.com/mlcommons/croissant.git
cd croissant/python/mlcroissant
python -m pip install ".[dev]"
```


Use `docker_build.sh` and `docker_run.sh` to set up the Web API.
Then go to http://localhost:8000/docs#/.



## To discuss
1. Add fields such as creator, keyword and dates into `mlcroissant` package: https://github.com/mlcommons/croissant/discussions/370
2. Add `Field.default_target` to Croissant?
3. Add `Field.ignored` to Croissant?
