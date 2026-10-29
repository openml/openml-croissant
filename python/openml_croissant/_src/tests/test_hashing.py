import pytest

from openml_croissant._src.hashing import ParquetHasher


@pytest.mark.parametrize(
    ("etag", "expected", "explanation"),
    [
        ("331ebc6b7fe7e996c676d2de5a5eb719", True, "Normal md5"),
        ("d41d8cd98f00b204e9800998ecf8427e", True, "Normal md5"),
        ("75723647a3985328b2cf535f27731c97-4", False, "Multipart file-upload"),
    ],
)
def test_is_etag(etag: str, expected: bool, explanation: str):
    actual = ParquetHasher._is_etag_md5(etag)
    assert actual == expected, explanation
