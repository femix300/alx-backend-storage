#!/usr/bin/env python3
'Writing strings to Redis'
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    '''Creates a Class Cache that writes a string to redis'''

    def __init__(self):
        '''Initializes the Cache Class'''
        self._redis = redis.Redis()

        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores data to redis alongsides a key'''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        if not self.exists(key):
            return None
        value = self._redis.get(key)

        if fn:
            return fn(value)

        return value

    def get_str(self, key: str):
        value = self._redis.get(key)
        return self.get(value, fn=lambda x: x.decode('utf-8'))

    def get_int(self, key: str):
        value = self._redis.get(key)
        try:
            return self.get(value, fn=lambda x: int(x))
        except Exception:
            return 0
