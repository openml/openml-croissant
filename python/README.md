# openml-croissant 🥐
Converting dataset metadata from OpenML to [Croissant](https://github.com/mlcommons/croissant) format

## Requirements
Python version 3.11.

If you do not have a Python environment:

```bash
    python3.11 -m venv venv
    source venv/bin/activate
```

## Install
```bash
python -m pip install ".[dev]"
```

Currently, you'll have to install the `mlcroissant` dependency manually, because PYPI is not
up-to-date.

```bash
mkdir dependencies
cd dependencies
git clone https://github.com/mlcommons/croissant.git
cd croissant/python/mlcroissant
python -m pip install ".[dev]"
```

Then, go back to the root directory of this project, and:

```bash
pre-commit install
```

## Run the API

```bash
PYTHONPATH=/path/to/project/openml-croissant/python ./openml_croissant/scripts/web_api.py
```

## Generate croissants locally

```bash
PYTHONPATH=/path/to/project/openml-croissant/python \
  ./openml_croissant/scripts/generate_croissants.py \
  -o /home/josvdvelde/projects/openml-croissant/output -c
```

## Run tests and other tools
From the root directory of the project:
```bash
pre-commit run --all-files
```
