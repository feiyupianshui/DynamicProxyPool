from utils import get_page
from pyquery import PyQuery as pq
import re


class ProxyMetaclass(type):#定义能通过一个指定的属性名称拿到类函数名列表和数量
    """
        元类，在FreeProxyGetter类中加入
        __CrawlFunc__和__CrawlFuncCount__
        两个参数，分别表示爬虫函数，和爬虫函数的数量。
    """
    def __new__(cls, name, bases, attrs):#参数attrs是类的方法合集
        count = 0
        attrs['__CrawlFunc__'] = [] #这个key的value是个列表
        for k, v in attrs.items(): #迭代所有方法
            if 'crawl_' in k: #如果方法名是以crawl_开头的
                attrs['__CrawlFunc__'].append(k) #作为这个key的value放入列表，注意append是个列表方法
                count += 1 #每放一个计数增加1
        attrs['__CrawlFuncCount__'] = count #最后的计数就是整数
        return type.__new__(cls, name, bases, attrs)


class FreeProxyGetter(object, metaclass=ProxyMetaclass):
    def get_raw_proxies(self, callback):#定义能通过名字调用下面这些爬虫函数的方法
        proxies = []
        print('Callback', callback)
        for proxy in eval("self.{}()".format(callback)): #将字符串str当成有效的表达式来求值并返回计算结果
            print('Getting', proxy, 'from', callback)
            proxies.append(proxy) #把拿到的代理都放入准备好的空列表
        return proxies #以列表形式返回爬到的所有代理

    def crawl_ip181(self):
        start_url = 'http://www.ip181.com/'
        html = get_page(start_url)
        ip_adress = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
        # \s* 匹配空格，起到换行作用
        re_ip_adress = ip_adress.findall(html)
        for adress,port in re_ip_adress:
            result = adress + ':' + port
            yield result.replace(' ', '')


    def crawl_ip3366(self):
        for page in range(1, 4):
            start_url = 'http://www.ip3366.net/free/?stype=1&page={}'.format(page)
            html = get_page(start_url)
            ip_adress = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            # \s * 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(html)
            for adress, port in re_ip_adress:
                result = adress+':'+ port
                yield result.replace(' ', '')


    def crawl_daili66(self, page_count=4):
        start_url = 'http://www.66ip.cn/{}.html'
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


    def crawl_goubanjia(self):
        start_url = 'http://www.goubanjia.com/free/gngn/index.shtml'
        html = get_page(start_url)
        if html:
            doc = pq(html)
            tds = doc('td.ip').items()
            for td in tds:
                td.find('p').remove()
                yield td.text().replace(' ', '')

    def crawl_data5u(self):
        for i in ['gngn', 'gnpt']:
            start_url = 'http://www.data5u.com/free/{}/index.shtml'.format(i)
            html = get_page(start_url)
            ip_adress = re.compile(' <ul class="l2">\s*<span><li>(.*?)</li></span>\s*<span style="width: 100px;"><li class=".*">(.*?)</li></span>')
            # \s * 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(html)
            for adress, port in re_ip_adress:
                result = adress+':'+port
                yield result.replace(' ','')

    def crawl_kxdaili(self):
        for i in range(1, 4):
            start_url = 'http://www.kxdaili.com/ipList/{}.html#ip'.format(i)
            html = get_page(start_url)
            ip_adress = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            # \s* 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(html)
            for adress, port in re_ip_adress:
                result = adress + ':' + port
                yield result.replace(' ', '')



