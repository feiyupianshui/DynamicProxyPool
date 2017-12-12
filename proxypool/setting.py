# Redis数据库的地址和端口
HOST = 'localhost'
PORT = 6666
DATABASE = 1

# 如果Redis有密码，则添加这句密码，否则设置为None或''
PASSWORD = '118667'

# 测试代理的网站
TEST_URL = "https://www.baidu.com/"

# 测试代理的超时时间
TEST_TIME = 9

# 数据库代理数量上下限，即数量在20-200之间的话，不会添加
OVERFLOW = 100
FLOOR = 20

# 检查休眠时间
CHECK_POOL_CYCLE = 20
VALID_PROXY_CYCLE = 600
