import redis

from proxypool.setting import HOST, PORT, DATABASE, PASSWORD
from .error import PoolEmptyError


class RedisClient(object):
    def __init__(self): # 这里可以不用传参，设置里的变量可以直接用
        if PASSWORD:
            self.client = redis.Redis(host=HOST, port=PORT, db=DATABASE, password=PASSWORD, decode_responses=True)
        else:
            self.client = redis.Redis(host=HOST, port=PORT, db=DATABASE, decode_responses=True)#不改为True就存为字节类型

    def push(self, proxy):
        self.client.rpush('proxies', proxy)

    def get(self, count=1): # 默认取一个
        part = self.client.lrange('proxies', 0, count-1)
        self.client.ltrim('proxies', count, -1)
        return part

    def pop(self):
        try:
            return self.client.rpop('proxies')
        except:
            return PoolEmptyError

    @property
    def length(self):
        return self.client.llen('proxies')

    def flush(self):
        self.client.flushall('proxies')

if __name__ == '__main__':
    conn = RedisClient()
    print(conn.pop())