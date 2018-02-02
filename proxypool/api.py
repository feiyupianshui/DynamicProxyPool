from flask import Flask, g
from .db import RedisClient

app = Flask(__name__)
def get_conn():
    if not hasattr(g, 'conn'):
        g.conn = RedisClient()
    return g.conn

@app.route('/')
def index():
    return '<h1>Welcome to Proxy Pool System</h1>'

@app.route('/get')
def get():
    con = get_conn()
    return con.pop()


@app.route('/random')
def get_proxy():
    """
    Get a proxy
    :return: 随机代理
    """
    conn = get_conn()
    return conn.random()

@app.route('/count')
def get_counts():
    """
    Get the count of proxies
    :return: 代理池总量
    """
    conn = get_conn()
    return str(conn.count())

if __name__ == '__main__':
    app.run()