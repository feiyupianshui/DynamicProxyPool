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
        while not self.overflowed:
            for i in range(self.crawl.__CrawlNum__):
                func_name = self.crawl.__CrawlFunc__[i]
                iterator = self.crawl.callback(func_name)
                self.tester.test_all(iterator)

    @property
    def overflowed(self):
        if self.conn.length >= OVERFLOW:
            return True
        else:
            return False





class Schedule(object):
    @staticmethod
    def valid_proxy(cycle=VALID_CHECK_CYCLE):#检查代理池中代理有效性的函数，参数是有效性的检查周期
        """
        Get half of proxies which in redis
        """
        conn = RedisClient()
        tester = ValidityTester()
        while True: #无限循环
            print('Refreshing ip')
            count = int(0.5 * conn.queue_len)
            if count == 0:
                print('Waiting for adding')
                time.sleep(cycle)#如果在代理池拿到的长度是0，先休眠等待
                continue
            raw_proxies = conn.get(count) #从redis中拿出一半数量的代理
            tester.set_raw_proxies(raw_proxies) #放入测试代理对象的接口函数
            tester.test() #启动有效性测试
            time.sleep(cycle) #满足条件就无限休眠

    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,#代理池数量下限  #检查代理池长度的函数
                   upper_threshold=POOL_UPPER_THRESHOLD,#队列数量上限
                   cycle=POOL_LEN_CHECK_CYCLE):#代理池长度检查的周期
        """
        If the number of proxies less than lower_threshold, add proxy
        """
        conn = RedisClient()
        adder = PoolAdder(upper_threshold)#实例化获取新代理的类要指定队列上限
        while True: #无限循环
            if conn.queue_len < lower_threshold:
                adder.add_to_queue()#如果代理池数量小于下限，就调用获取新代理函数
            time.sleep(cycle) #满足条件就无限休眠

    def run(self): #开启多进程同时检查代理有效性和监控代理池总数
        print('Ip processing running')
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        valid_process.start()
        check_process.start()
