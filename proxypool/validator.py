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
    def __init__(self):
        self.conn = RedisClient()

    async def test_one(self, proxy):
        try:
            async with aiohttp.ClientSession() as session:
                single_proxy = "http://" + proxy
                try:
                    async with session.get(TEST_URL, proxy=single_proxy, timeout=TEST_TIME) as response:
                        if response.status_code == 200:
                            self.conn.push(single_proxy)
                            print("valid proxy: {}.".format(proxy))
                except (ClientProxyConnectionError, TimeoutError, ValueError):
                    print("Invalid proxy: {}.".format(proxy))
        except (ClientConnectorError, ServerDisconnectedError, ClientResponseError) as e:
            print(e)


    def test_all(self, proxies=None):
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_one(proxy) for proxy in proxies]
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        except ValueError:
            print('Async error')







