
import redis

from alterego.config import config_register

__all__ = ['MemoryDriver', 'RedisDriver']


config_register('state_driver', 'redis')
config_register('redis', {
    'host': 'localhost',
    'port[int]': '6379',
    'db[int]': '0',
})


class BaseDriver(object):
    def append(self, key, value):
        raise NotImplementedError()


class MemoryDriver(BaseDriver):
    def __init__(self, config):
        config_ = config
        self.data = {}

    def append(self, key, value):
        if key not in self.data:
            values = self.data[key] = []
        else:
            values = self.data[key]
        values.append(value)


class RedisDriver(BaseDriver):
    def __init__(self, config):
        self.conn = redis.Redis(**config['redis'])

    def append(self, key, value):
        self.conn.append(key, value)
