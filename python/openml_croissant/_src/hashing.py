import typing

from botocore.exceptions import ClientError
from cachetools import Cache, TTLCache, cachedmethod

if typing.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

DATASET_BUCKET = "datasets"
A_WEEK_IN_SECONDS = 7 * 24 * 60 * 60


class ParquetHasher:
    """A class to return MD5 hashes for OpenML Parquet files."""

    def __init__(self, s3_client: S3Client):
        self._s3_client = s3_client
        self._cache: Cache = TTLCache(maxsize=10000, ttl=A_WEEK_IN_SECONDS)

    @cachedmethod(cache=lambda self: self._cache)
    def md5_from_s3_url(self, parquet_url: str) -> str | None:
        """
        Retrieve a MD5 hash from S3.

        The hashes are cached to improve the performance of subsequent calls. Parquet files should
        not change, so caching should be safe in normal circumstances. Only exception: when fixing
        errors in the Arff-to-Parquet conversion script. In that case, the Openml-Croissant
        instance should be restarted.
        """
        _, _, object_name = parquet_url.partition(DATASET_BUCKET)
        try:
            object_metadata = self._s3_client.head_object(Bucket=DATASET_BUCKET, Key=object_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise e
        md5_hash = object_metadata.get("ETag")
        if md5_hash is None:
            msg = "Could not determine MD5 hash from S3 URL"
            raise ValueError(msg)
        return md5_hash.strip('"')
