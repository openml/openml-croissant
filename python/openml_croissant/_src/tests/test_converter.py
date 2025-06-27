import json

import openml
import pytest
from pytest_mock import MockerFixture

import openml_croissant
from openml_croissant._src.hashing import ParquetHasher
from openml_croissant._src.tests.testutils import paths


def test_minimal_conversion():
    metadata_openml = openml.datasets.OpenMLDataset(
        dataset_id=1,
        name="anneal",
        description="description",
        licence="Public",
        citation="https://archive.ics.uci.edu/ml/citation_policy.html",
        url="https://example.com/dataset.arff",
        md5_checksum="checksum",
    )
    hasher = ParquetHasher(None)
    croissant = openml_croissant.convert(metadata_openml, openml_croissant.Settings(), hasher)
    assert croissant["name"] == "anneal"
    assert croissant["description"] == "description"
    assert croissant["url"] == "https://www.openml.org/d/1"
    assert croissant["license"] == "Public"
    assert croissant["citeAs"] == "https://archive.ics.uci.edu/ml/citation_policy.html"
    (distribution,) = croissant["distribution"]
    assert distribution["name"] == "data-file"
    assert distribution["description"] == "Data file belonging to the dataset."
    assert distribution["contentUrl"] == "https://example.com/dataset.arff"
    assert distribution["encodingFormat"] == [
        "text/plain",
        "https://ml.cms.waikato.ac.nz/weka/arff.html",
    ]
    assert distribution["md5"] == "checksum"


@pytest.mark.parametrize(
    ("features_xml", "input_json", "croissant_json"),
    [
        ("features_constructed.xml", "constructed.json", "constructed.json"),
        (
            "features_constructed.xml",
            "constructed_with_parquet.json",
            "constructed_with_parquet.json",
        ),
    ],
)
def test_constructed(
    mocker: MockerFixture,
    features_xml: str,
    input_json: str,
    croissant_json: str,
):
    file_path_features = paths.path_test_resources() / "openml" / features_xml
    file_path_json = paths.path_test_resources() / "openml" / input_json
    with file_path_json.open("r") as f:
        kwargs = json.load(f)
    metadata_openml = openml.datasets.OpenMLDataset(
        features_file=str(file_path_features),
        **kwargs,
    )
    hasher = ParquetHasher(None)
    mocker.patch.object(ParquetHasher, "md5_from_minio_url", return_value="mocked_hash")
    croissant_actual = openml_croissant.convert(
        metadata_openml,
        openml_croissant.Settings(),
        hasher,
    )

    expected_path = paths.path_test_resources() / "croissant" / croissant_json
    with expected_path.open("r") as f:
        croissant_expected = json.load(f, object_hook=openml_croissant.deserialize_croissant)

    # print(json.dumps(croissant_actual, indent=4, default=openml_croissant.serialize_croissant))
    assert croissant_actual == croissant_expected
