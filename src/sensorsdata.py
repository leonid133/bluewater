# -*- coding: utf-8 -*-
import redis
import json
from itertools import izip_longest, islice


class SensorsData:

    def __init__(self):
        self.redis = redis.Redis(host='bluewater-redis-master', port=6379)

    def __batcher(self, iterable, n):
        args = [iter(iterable)] * n
        return izip_longest(*args)

    def append(self, sec, data):
        key = "sensors_%s" % (sec)
        self.redis.hmset(key, data)

    def delete(self):
        for keybatch in self.__batcher(self.redis.scan_iter('sensors_*'), 500):
            self.redis.delete(*keybatch)

    def scan_keys(self, pattern, min_count=100):
        result = []
        cur, keys = self.redis.scan(cursor=0, match=pattern, count=min_count)
        result.extend(keys)
        while cur != 0:
            cur, keys = self.redis.scan(cursor=cur, match=pattern, count=min_count)
            result.extend(keys)

        return result

    def get(self, offset, limit, pattern):
        try:
            result = {}
            keys = sorted(self.scan_keys(pattern=pattern))[int(offset):(int(offset)+int(limit))]

            for key in keys:
                result[key] = (self.redis.hgetall(key))

            return result
        except Exception as e:
            return ['error', e.message]

    def get_latest(self, offset, limit, pattern):
        try:
            result = {}
            keys = list(reversed(sorted(self.scan_keys(pattern=pattern))))[int(offset):(int(offset)+int(limit))]

            for key in keys:
                result[key] = (self.redis.hgetall(key))

            return result
        except Exception as e:
            return ['error', e.message]