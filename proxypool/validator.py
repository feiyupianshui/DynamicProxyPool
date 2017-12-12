#!/use/bin/env python
#_*_coding:utf-8_*_

import asyncio
from asyncio import TimeoutError

import aiohttp
from aiohttp import ClientConnectionError as ClientProxyConnectionError, ClientConnectorError, ServerDisconnectedError
from aiohttp import ClientResponseError

from proxypool.db import RedisClient
from .setting import *


class ValidityTester(object):
    test_url = TEST_URL
    def __init__(self):
        self.conn = RedisClient()


    async def test_one(self, proxy):
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    if isinstance(proxy, bytes):
                        proxy = proxy.decode('utf-8')
                    single_proxy = "http://" + proxy
                    print('Testing:', single_proxy)
                    async with session.get(self.test_url, proxy=single_proxy, timeout=TEST_TIME) as response:
                        if response.status == 200:
                            self.conn.push(single_proxy)
                            print("valid proxy: {}.".format(proxy))
                except (ClientProxyConnectionError, TimeoutError, ValueError):
                    print("Invalid proxy: {}.".format(proxy))
        except (ClientConnectorError, ServerDisconnectedError, ClientResponseError) as e:
            print(e)


    def test_all(self, proxies):
        print('ValidityTester is working')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_one(proxy) for proxy in proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('Async error')







