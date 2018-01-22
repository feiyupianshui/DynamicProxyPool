# Redis数据库的地址和端口
REDIS_HOST = 'localhost'
REDIS_PORT = 'secret'
DATABASE = 1

# 如果Redis有密码，则添加这句密码，否则设置为None或''
PASSWORD = ''

# 测试代理的网站
TEST_URL = "https://www.baidu.com/"

REDIS_KEY = 'proxies'

# 代理分数
MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10

VALID_STATUS_CODES = [200, 302]

# 代理池数量界限
POOL_UPPER_THRESHOLD = 50000
