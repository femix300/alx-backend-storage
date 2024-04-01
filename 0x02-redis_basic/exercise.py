#!/usr/bin/env python3
'Writing strings to Redis'
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def replay(method: Callable):
    '''
    Display the history of calls of a particular function
    '''
    cache = redis.Redis()
    method_name = method.__qualname__

    inputs = f'{method_name}:inputs'
    outputs = f'{method_name}:outputs'

    inputs = cache.lrange(inputs, 0, -1)
    outputs = cache.lrange(outputs, 0, -1)

    print(f'{method_name} was called {len(inputs)} times:')
    for input_data, output_data in zip(inputs, outputs):
        print(f'{method_name}(*{input_data.decode()}) -> {output_data.decode()}')


def call_history(method: Callable) -> Callable:
    '''
    Decorator that stores the history of inputs and outputs
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        method_name = method.__qualname__

        input_key = f'{method_name}:inputs'
        output_key = f'{method_name}:outputs'

        self._redis.rpush(input_key, str(args))

        output = method(self, *args, **kwargs)

        self._redis.rpush(output_key, output)

        return output

    return wrapper


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

    @call_history
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
