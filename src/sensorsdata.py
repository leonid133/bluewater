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

    def get(self, offset=0, limit=100):
        try:
            keys = self.redis.scan(cursor=offset, match='sensors_*', count=limit)
            result = []
            for key in keys:
                result.append(json.loads(self.redis.get(key)))
            return result
        except:
            return []
