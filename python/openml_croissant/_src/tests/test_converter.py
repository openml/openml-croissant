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
    assert croissant["citation"] == "https://archive.ics.uci.edu/ml/citation_policy.html"
    (distribution,) = croissant["distribution"]
    assert distribution["name"] == "data-file"
    assert distribution["description"] == "Data file belonging to the dataset."
    assert distribution["contentUrl"] == "https://example.com/dataset.arff"
    assert distribution["encodingFormat"] == "text/plain"
    assert distribution["md5"] == "checksum"


def test_constructed():
    file_path_features = paths.path_test_resources() / "openml" / "features_constructed.xml"
    metadata_openml = openml.datasets.OpenMLDataset(
        name="test_name",
        description="Test Description",
        data_format="arff",  # UNUSED
        cache_format="pickle",  # UNUSED
        dataset_id=42,
        version=7,
        creator="Test Person, Another Person, And A Third",
        contributor="Another Test Person",
        collection_date="2020-01-01T00:01:02",
        upload_date="2021-01-01T00:01:02",
        language="English",
        licence="Public",
        original_data_url="https://example.com/original-url",
        url="https://example.com/data-file.arff",
        data_file="https://example.com/data-file.arff",  # Unused (legacy?)
        default_target_attribute="target",
        row_id_attribute="identifier",
        ignore_attribute=["identifier", "ignored_column"],
        version_label="Version label",  # Unused
        citation="Institute of Ontology",
        tag=["study_1", "study_41", "study_7", "study_88", "uci"],
        visibility="Public",  # Unused
        paper_url="https://example.com/paper-url",  # Unused
        update_comment="The dataset was uploaded when...",  # Unused
        md5_checksum="c45bb74cf7ac53ab2b9e61d105dbd454",
        features_file=str(file_path_features),
    )

    croissant_actual = openml_croissant.convert(metadata_openml, openml_croissant.Settings())

    expected_path = paths.path_test_resources() / "croissant" / "constructed.json"
    with expected_path.open("r") as f:
        croissant_expected = json.load(f, object_hook=openml_croissant.deserialize_croissant)

    # print(json.dumps(croissant_actual, indent=4, default=openml_croissant.serialize_croissant))
    assert croissant_actual == croissant_expected
