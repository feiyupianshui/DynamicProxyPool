import time
from multiprocessing import Process

from proxypool.error import ResourceDepletionError
from .db import RedisClient
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
        while not self.overflowed: # 双重循环
            for i in range(self.crawl.__CrawlNum__):
                func_name = self.crawl.__CrawlFunc__[i]
                proxy_list = self.crawl.callback(func_name)
                proxy_count += len(proxy_list)
                self.tester.test_all(proxy_list)
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
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            count = int(0.5 * conn.length)
            if count == 0:
                time.sleep(VALID_PROXY_CYCLE)
            proxies = conn.get(count)
            tester.test_all(proxies)
            time.sleep(VALID_PROXY_CYCLE)


    @staticmethod
    def check_pool():
        adder = PoolAdder()
        conn = RedisClient()
        while True: # 一个无限循环的检查
            if conn.length < FLOOR:
                adder.put()
            time.sleep(CHECK_POOL_CYCLE)

    def run(self): # 用子进程跑检查和验证程序
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        valid_process.start()
        check_process.start()

