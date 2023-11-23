#!/bin/bash

docker run --name openml-croissant \
  -p 8000:8000 \
  --rm \
  openml-croissant \
  python ./scripts/web_api.py --host "0.0.0.0" --port 8000
