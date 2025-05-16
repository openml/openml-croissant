# Releasing Openml Croissant
## Create release branch
Create a release branch from `main`, named `release/v[MAJOR].[MINOR].[PATCH].

## Update version and changelog
Update the version in [pyproject.tml](python/pyproject.toml). Check the CHANGELOG, and add the
release date.

## Merge
Merge back to `main`.

## Create a tag
Create a tag, named `v[MAJOR].[MINOR].[PATCH]`. A docker container will automatically be build
and published.

## Deploy
Deploy the new version to be used.
See [github openml-kube](https://github.com/openml-labs/openml-kube/blob/master/k8s_manifests/croissant-converter/croissant.yaml)
and [github documentation](https://github.com/openml/openml-internal-infra-wiki/blob/main/pages/kubernetes/kubernetes.md).
