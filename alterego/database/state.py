
import random
import string

import redis

from alterego.config import config_register

__all__ = ['MemoryDriver', 'RedisDriver']


config_register('state-driver', 'redis')
config_register('random', {
    'weight[int]': '66',
    'seed': random.sample(string.letters, 16)
})
config_register('redis', {
    'host': 'localhost',
    'port[int]': '6379',
    'db[int]': '0',
})


class BaseDriver(object):
    def __init__(self, config):
        self.config = config
        random_config = config['random']
        self.random_gen = random.Random(random_config['seed'])
        self.random_weight = random_config['weight']

    def append(self, key, value):
        raise NotImplementedError()

    def getall(self, key):
        raise NotImplementedError()

    def weighted_rand(self):
        if self.random_gen.randint(0, 100) < self.random_weight:
            return True
        return False

    def random(self, *keys):
        for key in keys:
            if self.weighted_rand():
                break
        else:
            key = self.random_key()
        try:
            return self.random_choice(self.getall(key))
        except IndexError:
            return self.random_garbage()

    def random_key(self):
        raise NotImplementedError()

    def random_choice(self, values):
        for value in values:
            if self.weighted_rand():
                return value
        return self.random_garbage()

    def random_garbage(self):
        garbage = ''
        letters = string.ascii_lowercase+'   '
        for idx_ in range(32):
            letter = self.random_gen.choice(letters)
            if letter == ' ':
                break
            garbage += letter
        return garbage


class MemoryDriver(BaseDriver):
    def __init__(self, config):
        BaseDriver.__init__(self, config)
        self._data = {}

    def append(self, key, value):
        if key not in self._data:
            values = self._data[key] = []
        else:
            values = self._data[key]
        values.append(value)

    def getall(self, key):
        return self._data[key]

    def random_key(self):
        return self.random_gen.choice(self._data.keys())


class RedisDriver(BaseDriver):
    def __init__(self, config):
        BaseDriver.__init__(self, config)
        self._conn = redis.Redis(**config['redis'])

    def append(self, key, value):
        self._conn.rpush(key, value)

    def getall(self, key):
        return self._conn.lrange(key, 0, -1)

    def random_key(self):
        return self._conn.randomkey()
