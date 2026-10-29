import logging
import re
import typing

from botocore.exceptions import ClientError
from cachetools import Cache, TTLCache, cachedmethod

if typing.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

DATASET_BUCKET = "datasets"
A_WEEK_IN_SECONDS = 7 * 24 * 60 * 60
ETAG_REGEX = re.compile(r"^[0-9a-f]{32}$")


class ParquetHasher:
    """A class to return MD5 hashes for OpenML Parquet files."""

    def __init__(self, s3_client: S3Client):
        self._s3_client = s3_client
        self._cache: Cache = TTLCache(maxsize=10000, ttl=A_WEEK_IN_SECONDS)

    @staticmethod
    def _is_etag_md5(etag: str) -> bool:
        """
        An ETAG does not have to be a MD5 hash. When multipart-upload was used, it can be a
        MD5 hash of the part, followed by the idx of the part.
        """
        if not etag or not isinstance(etag, str):
            return False
        return bool(ETAG_REGEX.match(etag))

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
        md5_hash = md5_hash.strip('"') if isinstance(md5_hash, str) else md5_hash
        if not ParquetHasher._is_etag_md5(md5_hash):
            msg = (
                "Could not determine MD5 hash from S3 URL. This is unexpected behavior, "
                "because the etag should always be a valid MD5 hash when we are not using "
                f"multipart-uploads. The ETAG was: {md5_hash}"
            )
            logging.error(msg)
            return None
        return md5_hash
