import json

import openml

import openml_croissant
from openml_croissant._src.tests.testutils import paths


def test_minimal_conversion():
    metadata_openml = openml.datasets.OpenMLDataset(
        dataset_id="1",
        name="anneal",
        description="description",
        licence="Public",
        citation="https://archive.ics.uci.edu/ml/citation_policy.html",
        url="https://example.com/dataset.arff",
        md5_checksum="checksum",
    )
    croissant = openml_croissant.convert(metadata_openml, openml_croissant.Settings())
    assert croissant["name"] == "anneal"
    assert croissant["description"] == "description"
    assert croissant["url"] == "https://www.openml.org/search?type=data&id=1"
    assert croissant["license"] == "Public"
    assert croissant["citeAs"] == "https://archive.ics.uci.edu/ml/citation_policy.html"
    (distribution,) = croissant["distribution"]
    assert distribution["name"] == "data-file"
    assert distribution["description"] == "Data file belonging to the dataset."
    assert distribution["contentUrl"] == "https://example.com/dataset.arff"
    assert distribution["encodingFormat"] == "text/plain"
    assert distribution["md5"] == "checksum"


def test_constructed():
    file_path_features = paths.path_test_resources() / "openml" / "features_constructed.xml"
    file_path_json = paths.path_test_resources() / "openml" / "constructed.json"
    with file_path_json.open("r") as f:
        kwargs = json.load(f)
    metadata_openml = openml.datasets.OpenMLDataset(
        features_file=str(file_path_features),
        **kwargs,
    )

    croissant_actual = openml_croissant.convert(metadata_openml, openml_croissant.Settings())

    expected_path = paths.path_test_resources() / "croissant" / "constructed.json"
    with expected_path.open("r") as f:
        croissant_expected = json.load(f, object_hook=openml_croissant.deserialize_croissant)

    # print(json.dumps(croissant_actual, indent=4, default=openml_croissant.serialize_croissant))
    assert croissant_actual == croissant_expected
