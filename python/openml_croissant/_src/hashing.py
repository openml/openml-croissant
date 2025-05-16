from cachetools import Cache, TTLCache, cachedmethod
from minio import Minio

DATASET_BUCKET = "datasets"
A_WEEK_IN_SECONDS = 7 * 24 * 60 * 60


class ParquetHasher:
    """A class to return MD5 hashes for OpenML Parquet files."""

    def __init__(self, minio: Minio):
        self._minio = minio
        self._cache: Cache = TTLCache(maxsize=10000, ttl=A_WEEK_IN_SECONDS)

    @cachedmethod(cache=lambda self: self._cache)
    def md5_from_minio_url(self, parquet_url: str):
        """
        Retrieve a MD5 hash from Minio.

        The hashes are cached to improve the performance of subsequent calls. Parquet files should
        not change, so caching should be safe in normal circumstances. Only exception: when fixing
        errors in the Arff-to-Parquet conversion script. In that case, the Openml-Croissant
        instance should be restarted.
        """
        _, _, object_name = parquet_url.partition(DATASET_BUCKET)
        stat_object = self._minio.stat_object(bucket_name=DATASET_BUCKET, object_name=object_name)
        return stat_object.etag
