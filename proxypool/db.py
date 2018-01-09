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

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

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