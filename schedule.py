import time
from multiprocessing import Process
from .db import RedisClient
from .error import ResourceDepletionError
from .getter import FreeProxyGetter
from .setting import *
from .validator import ValidityTester


class PoolAdder(object):
    def __init__(self):
        self.crawl = FreeProxyGetter()
        self.conn = RedisClient()
        self.tester = ValidityTester()

    def put(self):
        proxy_count = 0
        while not self.overflowed:
            for i in range(self.crawl.__CrawlNum__):
                func_name = self.crawl.__CrawlFunc__[i]
                iterator = self.crawl.callback(func_name)
                proxy_count += len(iterator)
                self.tester.test_all(iterator)
                if self.overflowed:
                    print('Have enough proxies already!')
                    break
        if proxy_count == 0:
            raise ResourceDepletionError

    @property
    def overflowed(self):
        if self.conn.length >= OVERFLOW:
            return True
        else:
            return False




class Schedule(object):
    @staticmethod
    def valid_proxy():
        pass

    @staticmethod
    def check_pool():
        pass

    def run(self):
        pass
