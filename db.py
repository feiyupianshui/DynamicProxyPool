import redis
from error import PoolEmptyError
from setting import HOST, PORT, PASSWORD


class RedisClient(object):
    def __init__(self, host=HOST, port=PORT):
        if PASSWORD:
            self._db = redis.Redis(host=host, port=port, password=PASSWORD, db=1)#连接redis并生成对象
        else:
            self._db = redis.Redis(host=host, port=port, db=1)

    def get(self, count=1):#拿出来
        """
        get proxies from redis
        """
        proxies = self._db.lrange("proxies", 0, count - 1)
        self._db.ltrim("proxies", count, -1) #修剪列表，只保留指定区间的值
        return proxies

    def put(self, proxy):#放进去
        """
        add proxy to right top
        """
        self._db.rpush("proxies", proxy)

    def pop(self):#扔了
        """
        get proxy from right.
        """
        try:
            return self._db.rpop("proxies").decode('utf-8')
        except:
            raise PoolEmptyError

    @property
    def queue_len(self):#返回长度
        """
        get length from queue.
        """
        return self._db.llen("proxies")

    def flush(self):#刷新
        """
        flush db
        """
        self._db.flushall()


if __name__ == '__main__':#这个应该是调试用的
    conn = RedisClient()
    print(conn.pop())
