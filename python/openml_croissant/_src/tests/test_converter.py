import mlcroissant as mlc
import openml

from openml_croissant._src import converter
from openml_croissant._src.tests.testutils import paths


def test_minimal_conversion():
    metadata_openml = openml.datasets.OpenMLDataset(
        dataset_id="1",
        name="anneal",
        description="description",
        licence="Public",
        citation="https://archive.ics.uci.edu/ml/citation_policy.html",
        data_file="https://example.com/dataset.arff",
        md5_checksum="checksum",
    )
    croissant = converter.convert(metadata_openml)
    assert croissant.name == "anneal"
    assert croissant.description == "description"
    assert croissant.url == "https://www.openml.org/search?type=data&id=1"
    assert croissant.license == "Public"
    assert croissant.citation == "https://archive.ics.uci.edu/ml/citation_policy.html"
    (distribution,) = croissant.distribution
    assert distribution.name == "data-file"
    assert distribution.description == "Data file belonging to the dataset."
    assert distribution.content_url == "https://example.com/dataset.arff"
    assert distribution.encoding_format == "text/plain"
    assert distribution.md5 == "checksum"


def test_constructed():
    file_path_features = paths.path_test_resources() / "openml" / "features_constructed.xml"
    metadata_openml = openml.datasets.OpenMLDataset(
        name="test_name",
        description="Test Description",
        data_format="arff",  # UNUSED
        cache_format="pickle",  # UNUSED
        dataset_id=42,  # UNUSED
        version=7,  # TODO NO PLACE ?
        creator="Test Person",  # TODO NO PLACE ?
        contributor="Another Test Person",  # TODO NO PLACE?
        collection_date="2020-01-01T00:01:02",  # TODO NO PLACE? test as 2020 or 28/02/1989
        upload_date="2021-01-01T00:01:02",  # TODO NO PLACE?
        language="English",  # TODO NO PLACE?s
        licence="Public",
        url="https://example.com/url",  # Unused
        default_target_attribute="target",
        row_id_attribute="identifier",
        ignore_attribute=["identifier", "ignored_column"],
        version_label="Version label",  # Unused
        citation="Institute of Ontology",
        tag=["study_1", "study_41", "study_7", "study_88", "uci"],  # Unused
        visibility=True,  # Unused
        original_data_url="https://example.com/original-url",  # Unused
        paper_url="https://example.com/paper-url",  # Unused
        update_comment="The dataset was uploaded when...",  # Unused
        md5_checksum="c45bb74cf7ac53ab2b9e61d105dbd454",
        data_file="https://example.com/data-file.arff",
        features_file=str(file_path_features),
        # minio_url=,
        # features_file: Optional[str] = None,
        # qualities_file: Optional[str] = None,
        # dataset = None,
        # parquet_file: Optional[str] = None
    )

    croissant_actual = converter.convert(metadata_openml)

    expected_path = paths.path_test_resources() / "croissant" / "constructed.json"
    issues = mlc.Issues()
    croissant_expected = mlc.Metadata.from_file(issues, expected_path)

    # print(json.dumps(croissant_actual.to_json(), indent=4))
    assert croissant_expected.to_json() == croissant_actual.to_json()
