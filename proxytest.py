#!/use/bin/env python
#_*_coding:utf-8_*_
import requests
from proxypool.setting import TEST_URL

proxy = '96.9.90.90:8080'

proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy,
}
