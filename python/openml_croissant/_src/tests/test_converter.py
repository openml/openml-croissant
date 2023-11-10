import openml

from openml_croissant._src import converter


def test_minimal_conversion():
    metadata_openml = openml.datasets.OpenMLDataset(
        name="anneal",
        description="description",
        url="https://example.com/dataset.pq",
        licence="Public",
        citation="https://archive.ics.uci.edu/ml/citation_policy.html",
    )
    croissant = converter.convert(metadata_openml)
    assert croissant.name == "anneal"
