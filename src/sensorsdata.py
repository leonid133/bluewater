# -*- coding: utf-8 -*-
import redis
import json


class SensorsData:

    def __init__(self):
        self.redis = redis.Redis(host='bluewater-redis-master', port=6379)

    def append(self, sec, usec, data):
        key = "sensors_%s_%s" % (sec, usec)
        self.redis.set(key, json.dumps(data))

    def delete(self):
        keys = self.redis.scan_iter('sensors_*')
        self.redis.delete(*keys)

    def scan_keys(self, offset=0, limit=100, pattern="sensors*"):
        result = []
        cur, keys = self.redis.scan(cursor=offset, match=pattern, count=limit)
        result.extend(keys)
        while cur != offset:
            cur, keys = self.redis.scan(cursor=cur, match=pattern, count=limit)
            result.extend(keys)

        return result

    def get(self, offset, limit, pattern):
        try:
            result = []
            for key in self.scan_keys(offset, limit, pattern):
                result.extend(json.loads(self.redis.get(key)))

            return result
        except:
            return []
