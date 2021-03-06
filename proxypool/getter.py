#!/use/bin/env python
#_*_coding:utf-8_*_

import requests
from pyquery import PyQuery as pq
import re
from requests.exceptions import ConnectionError


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        """
        :param cls: 当前类对象
        :param name: 类名
        :param bases: 父类集合
        :param attrs: 类方法合集
        :return: 增加返回爬虫函数名和数量的类属性(可通过实例调用）
        """
        attrs['__CrawlFunc__'] = []
        count = 0
        for k, v in attrs.items():
            if "crawl_" in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlNum__'] = count
        return type.__new__(cls, name, bases, attrs)

class FreeProxyGetter(object, metaclass=ProxyMetaclass):
    def callback(self, fun_name):
        proxys = []
        for proxy in eval('self.{}()'.format(fun_name)):
            proxys.append(proxy)
        return proxys

    def get_page(self, url, options={}):
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        headers = dict(base_headers, **options)
        try:
            response = requests.get(url, headers=headers) # 太久不写，连get都忘了
            if response.status_code == 200: # 连status_code都会错写成status
                # response.encoding = 'UTF-8' # 输出中文乱码了就去确认一下网页编码gb2312 or utf-8
                return response.text
        except ConnectionError:
            print('Requests '+url+' failed.')
            return None


    def crawl_66ip(self):
        for i in range(1, 4):
            start_url = 'http://www.66ip.cn/areaindex_21/{}.html'.format(i)#只要了四川的代理，每页数量也更多
            r = self.get_page(start_url)
            doc = pq(r)
            lis = doc('.containerbox table tr:gt(0)').items()
            for tr in lis:
                host = tr.find('td:nth-child(1)').text()
                port = tr.find('td:nth-child(2)').text()
                yield ':'.join([host, port])

    def crawl_goubanjia(self):
        for i in range(1, 4):
            start_url = 'http://www.goubanjia.com/free/gngn/index{}.shtml'.format(i)
            r = self.get_page(start_url)
            doc = pq(r)
            tds = doc('td.ip').items()
            for td in tds:
                td.find('p').remove()
                yield td.text().replace(' ', '')

    def crawl_data5u(self):
        for i in ['gngn', 'gnpt']:
            start_url = 'http://www.data5u.com/free/{}/index.shtml'.format(i)
            r = self.get_page(start_url)
            rule = re.compile(' <ul class="l2">\s*<span><li>(.*?)</li></span>\s*<span style="width: 100px;"><li class=".*?">(.*?)</li></span>')
            ip_list = rule.findall(r)
            for host, port in ip_list:
                ip_address = host + ':' + port
                yield ip_address.replace(' ', '')

    def crawl_kxdaili(self):
        for i in range(1, 4):
            start_url = 'http://www.kxdaili.com/ipList/{}.html#ip'.format(i)
            r = self.get_page(start_url)
            rule = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            ip_list = rule.findall(r)
            for host, port in ip_list:
                ip_adress = host + ':' + port
                yield ip_adress.replace(' ', '')

    def crawl_goubanjia(self):
        """
        获取Goubanjia
        :return: 代理
        """
        start_url = 'http://www.goubanjia.com/free/gngn/index.shtml'
        html = get_page(start_url)
        if html:
            doc = pq(html)
            tds = doc('td.ip').items()
            for td in tds:
                td.find('p').remove()
                yield td.text().replace(' ', '')

    def crawl_proxy360(self):
        """
        获取Proxy360
        :return: 代理
        """
        start_url = 'http://www.proxy360.cn/Region/China'
        print('Crawling', start_url)
        html = get_page(start_url)
        if html:
            doc = pq(html)
            lines = doc('div[name="list_proxy_ip"]').items()
            for line in lines:
                ip = line.find('.tbBottomLine:nth-child(1)').text()
                port = line.find('.tbBottomLine:nth-child(2)').text()
                yield ':'.join([ip, port])

    def crawl_daili66(self, page_count=4):
        """
        获取代理66
        :param page_count: 页码
        :return: 代理
        """
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])