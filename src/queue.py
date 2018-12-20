# -*- coding: utf-8 -*-

class DummyToiletQueue:

    def __init__(self):
        self.q = []

    def add(self, id):
        self.q.append(id)

    def get_my_status(self, id):
        try:
            ind = self.q.index(id)
            return ind
        except ValueError:
            return -1

    def remove(self):
        try:
            return self.q.pop(0)
        except IndexError:
            return -1

    def size(self):
        return len(self.q)
