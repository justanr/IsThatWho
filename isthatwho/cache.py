from datetime import timedelta
import json


def as_seconds(**kwargs):
    return int(timedelta(**kwargs).total_seconds())


class Cache:
    def __init__(self, cache, prefix, timeout=as_seconds(minutes=5), serializer=json):
        self._cache = cache
        self._prefix = '{prefix}::{{}}'.format(prefix=prefix)
        self._timeout = timeout
        self._serializer = serializer

    def get(self, key, default=None):
        result = self._cache.get(self._prefix.format(key))

        if result:
            return self._serializer.loads(result.decode('utf-8'))

        return default

    def set(self, key, value):
        self._cache.set(
            self._prefix.format(key),
            self._serializer.dumps(value).encode('utf-8'),
            ex=self._timeout
        )
