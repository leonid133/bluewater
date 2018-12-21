# -*- coding: utf-8 -*-
import redis
import json

class DummyToiletQueue:

    def __init__(self):
        self.redis = redis.Redis(host='bluewater-redis-master', port=6379)

    def add(self, id):
        q = self.get()
        q.append(id)
        self.__set(q)

    def get_my_status(self, id):
        q = self.get()
        try:
            ind = q.index(id)
            return ind
        except ValueError:
            return -1

    def remove(self):
        try:
            q = self.get()
            value = q.pop(0)
            self.__set(q)
            return value
        except IndexError:
            return -1

    def size(self):
        q = self.redis.get()
        return len(q)

    def __set(self, q):
        self.redis.set('state', json.dumps(q))

    def get(self):
        try:
            return json.loads(self.redis.get('state'))
        except:
            return []
