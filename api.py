from flask import Flask, g

from .db import RedisClient

__all__ = ['app']

app = Flask(__name__)


def get_conn():#获取客户端对象
    """
    Opens a new redis connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'redis_client'): #如果程序上下文找不到redis_client这个属性
        g.redis_client = RedisClient() #就创建连接
    return g.redis_client #直接从程序上下文获取与数据库的连接


@app.route('/')
def index():
    return '<h2>Welcome to Proxy Pool System</h2>'


@app.route('/get')
def get_proxy(): #返回一个代理
    """
    Get a proxy
    """
    conn = get_conn() #获取客户端对象
    return conn.pop() #取出来然后扔掉


@app.route('/count')
def get_counts(): #返回代理总数量
    """
    Get the count of proxies
    """
    conn = get_conn() #获取对象
    return str(conn.queue_len) #调用方法


if __name__ == '__main__':
    app.run()
