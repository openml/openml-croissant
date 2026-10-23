# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Changed from using the MinIO client towards using the boto3 client to talk with S3, so that we
  can migrate towards SeaweedFS instead of MinIO.
- Updated dependencies. Mainly `mlcroissant` to 1.1.1 from 1.0.17
### Removed
- Unused functionality, such as uploading files to MinIO, since we are generating Croissant
  files on the fly.

## [1.4.2] - 2025-06-27
### Fixed
- Change `url` from `/search?type=date&id=[ID]` to `/d/[ID]`

## [1.4.1] - 2025-06-20
### Fixed
- Openml: add environment variable `OPENML_SERVER` to the web api.

## [1.4.0] - 2025-06-20
### Changed
- Minio client: add environment variable `MINIO_CERT_CHECK` to optionally disable ssl
  certificate checks.
- Updated dependencies `uvicorn` (minor) and `cachetools` (mayor)

## [1.3.0] - 2025-05-16
### Changed
- Using parquet instead of arff files
- Updated `mlcroissant` from 1.0.16 to 1.0.17

## [1.2.0] - 2025-03-06
Start of this changelog
