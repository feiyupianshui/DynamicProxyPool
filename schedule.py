import time
from multiprocessing import Process #多进程
import asyncio #支持异步IO的协程模块
import aiohttp
try:
    from aiohttp.errors import ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
from db import RedisClient
from error import ResourceDepletionError
from getter import FreeProxyGetter
from setting import *
from asyncio import TimeoutError


class ValidityTester(object): #检测代理有效性
    test_api = TEST_API #来自setting文件

    def __init__(self):
        self._raw_proxies = None #定义默认为空的初始值
        self._usable_proxies = [] #定义默认为空的结果，数据结构为列表
        self._conn = RedisClient()


    async def test_single_proxy(self, proxy): #定义测试单个代理的协程，参数在扔进循环的时候放入
        """
        text one proxy, if valid, put them to usable_proxies.
        """
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    if isinstance(proxy, bytes):
                        proxy = proxy.decode('utf-8')
                    real_proxy = 'http://' + proxy #检查并规范待检测代理的格式
                    print('Testing', proxy)                             #请求超时时间来自setting文件手动指定
                    async with session.get(self.test_api, proxy=real_proxy, timeout=get_proxy_timeout) as response: #定义发起异步HTTP请求的协程
                        if response.status == 200:
                            self._conn.put(proxy) #有响应的就放入数据库
                            print('Valid proxy', proxy) #并在控制台返回
                except (ProxyConnectionError, TimeoutError, ValueError):#python自带异常，传入无效参数时会报ValueError
                    print('Invalid proxy', proxy) #连接各种报错的就打印出来说一下
        except (ServerDisconnectedError, ClientResponseError,ClientConnectorError) as s:#层层捕捉可能出现的报错
            print(s)
            pass

    def test(self, proxies):#并发测试代理
        """
        aio test all proxies.
        """
        print('ValidityTester is working')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_single_proxy(proxy) for proxy in proxies]#把代理一个个都放入测试的协程，扔进循环事件实现并发测试
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('Async Error') #捕捉无效参数报错


class PoolAdder(object): #获取新代理，放入代理池
    """
    add proxy to pool
    """

    def __init__(self, threshold): #整合了三个工具（类）
        self._threshold = threshold #代理队列数量上限，可在setting中导入然后传入
        self._conn = RedisClient() #数据库对象
        self._tester = ValidityTester() #测试代理有效性的对象
        self._crawler = FreeProxyGetter() #爬取代理的对象

    def is_over_threshold(self): #不让数据库数量溢出，保持小于上限
        """
        judge if count is overflow.
        """
        if self._conn.queue_len >= self._threshold:
            return True
        else:
            return False

    def add_to_queue(self):#获取新的代理队列
        print('PoolAdder is working')
        proxy_count = 0 #新队列初始个数设为0
        while not self.is_over_threshold(): #如果没有溢出
            for callback_label in range(self._crawler.__CrawlFuncCount__):#循环函数总数量，用索引到列表里调函数名
                callback = self._crawler.__CrawlFunc__[callback_label]#按索引取出爬取函数
                raw_proxies = self._crawler.get_raw_proxies(callback)#用函数名调用函数并拿到返回的代理列表
                # test crawled proxies
                self._tester.test(raw_proxies)#启动测试，合格的会被自动放入数据库
                proxy_count += len(raw_proxies)#拿到的代理总数
                if self.is_over_threshold():#检测数据量的代理数量是否溢出
                    print('IP is enough, waiting to be used')
                    break
            if proxy_count == 0:
                raise ResourceDepletionError#这是一个都没爬到？


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
