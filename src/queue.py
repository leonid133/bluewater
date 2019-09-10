# -*- coding: utf-8 -*-
import redis
import json
from Queue import Queue
from threading import Lock

class DummyToiletQueue:

    def __init__(self):
        # self.redis = redis.Redis(host='bluewater-redis-master', port=6379)
        self.queue = Queue()
        self.lock = Lock()

    def add(self, id):
        # q = self.get()
        # q.append(id)
        # self.__set(q)
        self.lock.acquire()
        try:
            self.queue.put(id)
        finally:
            self.lock.release()

    def get_my_status(self, id):
        # q = self.get()
        # try:
        #     ind = q.index(id)
        #     return ind
        # except ValueError:
        #     return -1
        try:
            return self.list.index(id)
        except ValueError:
            return -1

    def remove(self):
        # try:
        #     q = self.get()
        #     value = q.pop(0)
        #     self.__set(q)
        #     return value
        # except IndexError:
        #     return -1
        self.lock.acquire()
        try:
            id = self.queue.get(False)
            if id:
                return id
            return -1
        except Exception as e:
            return -1
        finally:
            self.lock.release()

    def size(self):
        # q = self.redis.get()
        # return len(q)
        return self.queue.qsize()

    # def __set(self, q):
    #     self.redis.set('state', json.dumps(q))
    #
    def get(self):
        try:
            return json.loads(self.queue.qsize())
        except:
            return []
