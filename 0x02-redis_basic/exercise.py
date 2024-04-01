#!/usr/bin/env python3
'Writing strings to Redis'
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
    Decorator that counts the number of times a method is called
    '''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    '''Creates a Class Cache that writes a string to redis'''

    def __init__(self):
        '''Initializes the Cache Class'''
        self._redis = redis.Redis()

        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores data to redis alongsides a key'''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> \
            Union[str, bytes, int, float]:
        if not self._redis.exists(key):
            return None
        value = self._redis.get(key)

        if fn:
            return fn(value)

        return value

    def get_str(self, key: str) -> str:
        value = self._redis.get(key)
        return self.get(value, fn=lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        value = self._redis.get(key)
        try:
            return self.get(value, fn=lambda x: int(x))
        except Exception:
            return 0
