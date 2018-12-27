# -*- coding: utf-8 -*-
import redis
import json
from itertools import izip_longest, islice


class SensorsData:

    def __init__(self):
        self.redis = redis.Redis(host='bluewater-redis-master', port=6379)

    def append(self, sec, usec, data):
        key = "sensors_%s_%s" % (sec, usec)
        self.redis.set(key, json.dumps(data))

    def __batcher(self, iterable, n):
        args = [iter(iterable)] * n
        return izip_longest(*args)

    def delete(self):
        for keybatch in self.__batcher(self.redis.scan_iter('sensors_*'), 500):
            self.redis.delete(*keybatch)

    def get(self, offset=0, limit=100):
        try:
            keys = islice(self.redis.scan_iter('sensors_*'), offset, offset + limit, 1)
            for key in keys:
                yield json.loads(self.redis.get(key))
        except:
            pass
