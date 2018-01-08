import redis

from proxypool.setting import HOST, PORT, DATABASE, PASSWORD, REDIS_KEY
from .error import PoolEmptyError


class RedisClient(object):
    def __init__(self): # 这里可以不用传参，设置里的变量可以直接用
        if PASSWORD:
            self.client = redis.Redis(host=HOST, port=PORT, db=DATABASE, password=PASSWORD, decode_responses=True)
        else:
            self.client = redis.Redis(host=HOST, port=PORT, db=DATABASE, decode_responses=True)#不改为True就存为字节类型

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)

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