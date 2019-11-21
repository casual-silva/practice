# -*- coding: utf-8 -*-

"""AVNET整站数据爬虫

用于获取AVNET整站型号数据

requirements:
    scrapy>=1.2.0
    lxml
"""

__author__ = "qaulau"

import os
import re
import sys
import time
import json
import copy
import math
import base64
import urllib
import argparse
import urlparse
import random
import logging
import hashlib
from Queue import Queue

try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy
import requests
# six
from six.moves.urllib.request import getproxies, proxy_bypass
from six.moves.urllib.parse import unquote
from six.moves.urllib.parse import urlunparse
# scrapy import
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import DropItem, IgnoreRequest, CloseSpider, NotConfigured
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.utils.python import to_bytes
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.reqser import request_to_dict, request_from_dict
# lxml
import lxml.html

sys.__APP_LOG__ = False
try:
    import config
except ImportError:
    sys.path[0] = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
    import config
import packages.Util as util
from packages import hqchip

logger = logging.getLogger(__name__)

queue = Queue()

settings = {
    'BOT_NAME': 'hqchipbot',
    'ROBOTSTXT_OBEY': False,
    'COOKIES_ENABLED': True,
    'CONCURRENT_ITEMS': 100,
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_TIMEOUT': 30,
    'DOWNLOAD_DELAY': 2,

    'DEFAULT_REQUEST_HEADERS': {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.avnet.com',
        'Referer': 'https://www.avnet.com/shop/AllProducts?countryId=us&deflangId=-1&catalogId=10001&langId=-1&storeId=715839035',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'DOWNLOADER_MIDDLEWARES': {
        __name__ + '.IgnoreRquestMiddleware': 1,
        __name__ + '.UniqueRequestMiddleware': 3,
        __name__ + '.RandomUserAgentMiddleware': 5,
        __name__ + '.ProxyRequestMiddleware': 8,
    },
    'ITEM_PIPELINES': {
        __name__ + '.MetaItemPipeline': 500,
    },
    'EXTENSIONS': {
        'scrapy.extensions.closespider.CloseSpider': 500,
    },
    'TELNETCONSOLE_ENABLED': False,
    'LOG_LEVEL': logging.DEBUG,
    'USE_PROXY': '',
}
# 过滤规则
filter_rules = (
    '/shop/us/c/([a-zA-Z0-9\-/]+)\?listing=true',
    '/search/resources/store/',
    '/wcs/resources/store/',
)


class RandomUserAgentMiddleware(object):
    """随机UserAgent中间件"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        if 'USER_AGENT_LIST' in crawler.settings:
            agents = crawler.settings.getlist('USER_AGENT_LIST')
        else:
            agents = config.USER_AGENT_LIST
        return cls(agents)

    def process_request(self, request, spider):
        if self.agents:
            request.headers.setdefault('User-Agent', random.choice(self.agents))


class IgnoreRquestMiddleware(object):
    """忽略请求url"""

    def __init__(self, crawler):
        global filter_rules
        self.filters = []
        for rule in filter_rules:
            self.filters.append(re.compile(rule))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        _ignore = True
        for vo in self.filters:
            if vo.search(request.url) or request.url in spider.start_urls:
                _ignore = False
                break
        if _ignore:
            raise IgnoreRequest("ingore orther url: %s" % request.url)


class UniqueRequestMiddleware(object):
    """去重请求中间件"""
    name = 'avnet'

    def __init__(self, crawler):
        # self.mongo = crawler.spider.mongo
        self.mongo = hqchip.db.mongo['spider_' + self.name + '_urls']

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def close_spider(self, spider):
        del self.mongo

    def process_request(self, request, spider):
        url = to_bytes(request.url.split('#')[0])
        key = hashlib.md5(url).hexdigest()
        info = self.mongo.find_one({'key': key})
        if info:
            logger.warn("---ingore repeat url---: %s" % request.url)
            raise IgnoreRequest("ingore repeat url: %s" % request.url)


class ProxyRequestMiddleware(object):
    """代理请求中间件"""

    def __init__(self, crawler):
        if not settings['USE_PROXY']:
            raise NotConfigured

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def close_spider(self, spider):
        pass

    def process_request(self, request, spider):
        proxy = None
        self.get_web_proxy()
        try:
            proxy = queue.get()
        except:
            pass
        proxies = {}
        try:
            proxies['http'] = self._get_proxy(proxy, 'http')
            proxies['https'] = self._get_proxy(proxy, 'https')
        except:
            pass
        self._set_proxy(request, proxies)

    def _get_proxy(self, url, orig_type):
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlparse.urlunparse((proxy_type or orig_type, hostport, '', '', '', ''))
        if user:
            user_pass = to_bytes(
                '%s:%s' % (unquote(user), unquote(password)),
                encoding=self.auth_encoding)
            creds = base64.b64encode(user_pass).strip()
        else:
            creds = None
        return creds, proxy_url

    def _set_proxy(self, request, proxies):
        if not proxies:
            return
        parsed = urlparse_cached(request)
        scheme = parsed.scheme
        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return
        if scheme not in proxies:
            return
        creds, proxy = proxies[scheme]
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = b'Basic ' + creds

    def get_web_proxy(self):
        '''
        从指定接口获取代理ip
        :return:  代理数量, 代理列表
        '''
        if queue.qsize() > 0:
            return
        rs = requests.get(url='http://proxy.elecfans.net/proxys.php?key=AXw1KwWIsK&num=10')
        proxy = json.loads(rs.content)
        for vo in proxy['data']:
            queue.put(vo['ip'])

class GoodsItem(scrapy.Item):
    goods_sn = scrapy.Field()  # 产品标识
    goods_name = scrapy.Field()  # 产品销售型号名
    url = scrapy.Field()  # URL
    goods_img = scrapy.Field()  # 产品图片
    goods_thumb = scrapy.Field()  # 缩略图
    goods_desc = scrapy.Field()  # 描述
    provider_name = scrapy.Field()  # 供应商/品牌
    provider_url = scrapy.Field()  # 供应商URL
    tiered = scrapy.Field()  # 价格阶梯
    stock = scrapy.Field()  # 库存信息，库存和最小购买量
    increment = scrapy.Field()  # 递增量
    doc = scrapy.Field()  # 文档
    attr = scrapy.Field()  # 属性
    rohs = scrapy.Field()  # rohs
    catlog = scrapy.Field()  # 分类
    id = scrapy.Field()  # 产品供应商id=16
    # key = scrapy.Field() #
    goods_other_name = scrapy.Field()
    region = scrapy.Field()


class MetaItemPipeline(object):
    """数据集管道"""

    def __init__(self, crawler):
        name = 'spider_' + crawler.spider.name + '_item'
        self.mongo = hqchip.db.mongo[name]
        self.mongo.ensure_index('key', unique=True)
        self.mongo.ensure_index('goods_sn', unique=False)
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        """保存数据"""
        if not item:
            raise DropItem("item data type error")
        data = copy.deepcopy(dict(item))
        if not data:
            raise DropItem("item data is empty")
        data['url'] = to_bytes(item['url'].split('#')[0])
        data['key'] = hashlib.md5(data['url']).hexdigest()
        info = self.mongo.find_one({'goods_sn': data['goods_sn']})
        if not info:
            self.mongo.insert(data)
            logger.info('success insert mongodb : %s' % data['key'])
        elif data['tiered'][0][0] > 0:
            self.mongo.update({'_id': info['_id']}, {"$set": data})
            logger.info('success update mongodb : %s' % data['key'])
        self.count += 1
        raise DropItem('success process')

    def close_spider(self, spider):
        print '本次获取{0}条数据'.format(self.count)
        del self.mongo


class HQChipSpider(CrawlSpider):
    """AVNET 蜘蛛"""
    name = 'avnet'
    allowed_domains = ['www.avnet.com']
    start_urls = ['https://www.avnet.com/shop/AllProducts?countryId=us&catalogId=10001&langId=-1&storeId=715839035&deflangId=-1']
    # start_urls = ['https://www.avnet.com/shop/us/c/discretes/bipolar-transistors/rf-bjts/']
    base_url = 'https://www.avnet.com/shop/us/'

    def __init__(self, name=None, **kwargs):
        self._init_args(**kwargs)
        super(HQChipSpider, self).__init__(name, **kwargs)

    def _init_args(self, **kwargs):
        start_url = kwargs.get('START_URL', '')
        if start_url:
            self.start_urls = [start_url]
        self.re_wc_js  = re.compile('WCParamJS\s=\s([^;]+)')
        self.boostquery = 'obsoleteFlag:%22NO%22%5E599999.0%20price_USD:%7B0.00001%20TO%20*%7D%5E499999.0%20' \
                          'inStock:%22true%22%5E9000.0%20topSellerFlag:%22Yes%22%5E0.085%20newProductFlag:' \
                          '%22Yes%22%5E0.080%20packageTypeCode:%22BKN%22%5E0.075'
        self.limit_num = 50
        self.interval = 0.5
        self.mongo = hqchip.db.mongo['spider_' + self.name + '_urls']
        self.mongo.ensure_index('key', unique=True)
        self._start_index = int(kwargs.get('START_INDEX', 0))
        self._end_index = int(kwargs.get('END_INDEX', 0))

    def start_requests(self):
        url  = self.start_urls[0]
        headers = settings['DEFAULT_REQUEST_HEADERS'].copy()
        headers['User-Agent'] = settings['USER_AGENT']
        headers['referer'] = 'https://www.avnet.com/wps/portal/us'
        # #单个测试
        # if '/shop/us/c/' in url:
        #     yield Request(url, callback=self.parse_resp)
        #     return
        resp = requests.get(url, headers=headers, timeout=15)
        root = lxml.html.fromstring(resp.text.encode('utf-8'))
        # 获取分类url
        links = root.xpath('//ul[@class="products collapse in"]/li/ul/li')
        links_list = []
        for flag in links:
            signs = flag.xpath('./ul[@class="level-2"]/li/a/@href')
            if signs:
                links_list += signs
            else:
                links_list.append(flag.xpath('./a')[0].attrib['href'])
        # 修改为直接获取一级分类url
        # links_list = root.xpath('//div[@class ="category-header"]/div/h4/a/@href')
        headers['referer'] = url
        cookies = {}
        for vo in resp.cookies:
            cookies[vo.name] = vo.value
        if (self._start_index + 1) > len(links_list):
            return
        if self._end_index:
            dlinks = links_list[self._start_index:self._end_index]
        else:
            dlinks = links_list[self._start_index:]
        for link in dlinks:
            url = link + '?listing=true'
            yield Request(url, headers=headers, cookies={}, callback=self.parse_resp)
            time.sleep(self.interval)

    def parse_resp(self, resp):
        if '/search/resources/store/' in resp.url:
            for vo in self.parse_list(resp):
                yield vo
        elif '/shop/us/c/' in resp.url:
            match = self.re_wc_js.search(resp.body)
            if not match:
                print 'URL:{0}---not match resp.body'.format(resp.url)
                return
            wcjs = match.group(1).replace("\n", '').replace("\t", '').replace("\r", '').replace("  ", '')\
                .replace('\'', '"').replace(',}', '}')
            wcjs = json.loads(wcjs)
            params = {
                'searchType': '100',
                'profileName': 'Avn_findProductsByCategory_Summary',
                'searchSource': 'Q',
                'storeId': wcjs['storeId'],
                'catalogId': wcjs['catalogId'],
                'langId': wcjs['langId'],
                'contractId': wcjs['contractId'],
                'responseFormat': 'json',
                # 'onlyShow': 'inStock%3A%22true%22',
                'pageSize': 60,
                'pageNumber': 1,
                'wt': 'json',
            }
            pageid = resp.xpath("//meta[@name='pageId']/@content").extract()[0]
            url = '/search/resources/store/{0}/productview/byCategory/{1}?{2}&_wcf.search.internal.boostquery={3}'.format(
                wcjs['storeId'], pageid, urllib.urlencode(params), self.boostquery)
            url = urlparse.urljoin(self.base_url, url)
            headers = settings['DEFAULT_REQUEST_HEADERS'].copy()
            headers['referer'] = url
            yield Request(url, meta={'params': params, 'pageid': pageid, 'referer': resp.url}, headers=headers,
                          cookies={}, callback=self.parse_resp)

    def parse_list(self, resp):
        """解析列表数据"""
        meta = resp.meta
        params = meta['params']
        headers = settings['DEFAULT_REQUEST_HEADERS'].copy()
        headers['referer'] = meta['referer']
        try:
            data = json.loads(resp.body)
        except:
            time.sleep(3)
            raise NotConfigured('{0}--Json_loads_error'.format(resp.url))
        total = int(data['recordSetTotal'])
        psize = int(data['recordSetCount'])
        pnum  = meta.get('pagenum', 1)
        tpnum = int(math.ceil(total * 1.0 / psize))
        if pnum > 1:
            url = to_bytes(resp.url.split('#')[0])
            key = hashlib.md5(url).hexdigest()
            mdata = {
                'key': key,
                'url': url,
            }
            try:
                self.mongo.insert(mdata)
            except:
                pass
        # 分类
        category = {}
        if 'categoryList' in data['CategoryHierarchyView']:
            for cates in data['CategoryHierarchyView']['categoryList']:
                for vo in cates:
                    category[vo['categoryId']] = vo['label']
        for vo in data['breadCrumbTrailEntryView']:
            category[vo['value']] = vo['label']
        # 解析详情数据
        items = []
        for vo in data['catalogEntryView']:
            item = self.parse_detail(vo, category)
            if item:
                items.append(item)
        # 获取价格信息
        start = 0
        limit = 10
        while 1:
            catalogEntrys = items[start:start + limit]
            catalogEntryId = ''
            for vo in catalogEntrys:
                catalogEntryId += '&{0}={1}'.format('catalogEntryId', vo['goods_sn'])
            url = '/wcs/resources/store/{0}/price?q=byCatalogEntryIds&currency=USD&profileName=' \
                  'IBM_Store_EntitledPrice_RangePrice_All&contractId={1}{2}'.format(params['storeId'], params['contractId'],
                                                                                     catalogEntryId)
            url = urlparse.urljoin(self.base_url, url)
            yield Request(url, callback=self.parse_price, meta={'items': catalogEntrys}, headers=headers, cookies={})
            if len(catalogEntrys) < limit:
                break
            start += limit
            time.sleep(self.interval)
        if pnum == 1 and tpnum > 1:
            for i in xrange(2, tpnum + 1):

                params['pageNumber'] = i
                url = '/search/resources/store/{0}/productview/byCategory/{1}?{2}&_wcf.search.internal.boostquery={3}' \
                      '&showMore=true&intentSearchTerm=*&searchTerm=*'.format(
                    params['storeId'], meta['pageid'], urllib.urlencode(params), self.boostquery)
                url = urlparse.urljoin(self.base_url, url)
                # 跳过页码中有2的页面
                # if '2' in str(i):
                #     logger.info('page_have_2 pass! url:{0}'.format(headers['referer']))
                #     continue
                yield Request(url, meta={'params': params, 'pageid': meta['pageid'], 'pagenum': i, 'referer': meta['referer']},
                              cookies={}, callback=self.parse_resp, headers=headers)
                time.sleep(self.interval)

    def parse_detail(self, data, category=None):
        """解析系列型号数据"""
        if category is None:
            category = {}
        item = GoodsItem()
        item['url'] = urlparse.urljoin(self.base_url, data['avn_pdp_seo_path'])
        item['goods_sn'] = data['uniqueID']
        item['goods_name'] = data['mfPartNumber_ntk'].upper()
        if not item['goods_name']:
            return None
        if 'packageTypeCode' in item:
            item['goods_other_name'] = '{0}/{1}'.format(item['goods_name'], item['packageTypeCode']).upper()
        item['provider_name'] = data['manufacturer']
        item['provider_url'] = ''
        item['goods_desc'] = data['shortDescription'] if 'shortDescription' in data else ''
        if 'avn_thumbnail' in data and data['avn_thumbnail']:
            item['goods_thumb'] = util.urljoin(self.base_url, data['avn_thumbnail'])
        else:
            item['goods_thumb'] = ''
        item['goods_img'] = item['goods_thumb'].replace('icon_thumb', 'icon_web')
        if 'auxDescription2' in data and data['auxDescription2']:
            item['doc'] = data['auxDescription2']
        else:
            item['doc'] = ''
        min_qty = int(data['xcatField1']) if 'xcatField1' in data else 1
        if 'multQuantity' in data:
            increment = int(data['multQuantity'])
        else:
            increment = 1
        if 'inv_strlocqty' in data:
            stock_qty = util.intval(data['inv_strlocqty'])
        else:
            stock_qty = 0
        item['rohs'] = 1 if 'ROHSComplianceCode' in data and data['ROHSComplianceCode'] == 'Y' else 0
        item['tiered'] = [[0, 0.0]]
        item['stock'] = [stock_qty, min_qty]  # 库存
        item['increment'] = increment
        # 属性
        item['attr'] = []
        if 'attributes' not in data:
            data['attributes'] = []
        for vo in data['attributes']:
            try:
                item['attr'].append([vo['name'], vo['values'][0]['value']])
            except:
                pass
        # 分类
        item['catlog'] = []
        catelogs = data['parentCatgroup_id_path'].split('_')[-1].split(':')
        for vo in catelogs:
            if vo not in category:
                continue
            item['catlog'].append((category[vo], vo))
        item['region'] = 'AMERICAS'
        item['id'] = 16
        return item

    def parse_price(self, resp):
        """解析库存价格数据"""
        items = resp.meta.get('items')
        if not items:
            logger.error('request meta data error, url: %s', resp.url)
            return
        prices = {}
        try:
            data = json.loads(resp.body)
            for entprice in data['EntitledPrice']:
                tiered = []
                if 'RangePrice' not in entprice:
                    entprice['RangePrice'] = []
                for vo in entprice['RangePrice']:
                    qty = util.intval(vo['minimumQuantity']['value']) if 'minimumQuantity' in vo else 1
                    price = util.floatval(vo['priceInRange']['value']) if 'priceInRange' in vo else 0
                    if not qty or (tiered and qty < tiered[-1][0]):
                        continue
                    tiered.append([qty, price])
                if not tiered:
                    tiered.append([0, 0.0])
                prices[entprice['productId']] = tiered
        except:
            logger.exception('parse stock price error, url: {0}---price_Json_error---{1}'.format(resp.url, resp.body) )
        for item in items:
            if item['goods_sn'] in prices:
                item['tiered'] = prices[item['goods_sn']]
            yield item


    @property
    def closed(self):
        """蜘蛛关闭清理操作"""

        def wrap(reason):
            pass

        return wrap


def main():
    global settings
    from scrapy import cmdline
    from scrapy.settings import Settings

    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('-h', '--help', dest='help', help='获取帮助信息',
                        action='store_true', default=False)

    act_group = parser.add_argument_group(title='操作选项组')
    act_group.add_argument('-r', '--run', dest='cmd', help='运行爬虫获取数据',
                           action='store_const', const='runspider')
    act_group.add_argument('-s', '--shell', dest='cmd', help='控制台调试',
                           action='store_const', const='shell')
    act_group.add_argument('-v', '--view', dest='cmd', help='使用浏览器打开蜘蛛获取的URL页面',
                           action='store_const', const='view')

    run_group = parser.add_argument_group(title='运行操作组')
    run_group.add_argument('-n', '--limit-num', dest='limit', default=0,
                           help='限制总请求次数，默认为0不限制', type=int)
    run_group.add_argument('-m', '--max-request-num', dest='max', default=30,
                           help='同时最大请求数，默认为30，0则不限制', type=int)
    run_group.add_argument("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                           help="设置爬虫参数（可以重复）")
    run_group.add_argument("-o", "--output", metavar="FILE",
                           help="输出 items 结果集 值FILE (使用 -o 将定向至 stdout)")
    run_group.add_argument("-t", "--output-format", metavar="FORMAT",
                           help="基于 -o 选项，使用指定格式输出 items")
    run_group.add_argument('-d', '--dist', help='分布式运行，用于其他进程提交数据',
                           action='store_true', default=False)
    run_group.add_argument('-p', '--proxy', help='使用代理进行请求', action='store_true', default=False)

    opt_group = parser.add_argument_group(title='可选项操作组')
    opt_group.add_argument('-S', '--start-index', default=0, help='设置起始分类索引值，默认0', type=int)
    opt_group.add_argument('-E', '--end-index', default=None, help='设置截止分类索引值，默认不限', type=int)

    gen_group = parser.add_argument_group(title='通用选择项')
    gen_group.add_argument('-u', '--url', help='设置URL，运行操作设置该项则为起始爬取URL，\
                                                                    调试操作设置则为调试URL，查看操作则为打开查看URL')

    args = parser.parse_args()
    if args.help:
        parser.print_help()
    elif args.cmd:
        settings = Settings(settings)
        if args.cmd == 'runspider':
            argv = [sys.argv[0], args.cmd, sys.argv[0]]
            for vo in run_group._group_actions:
                opt = vo.option_strings[0]
                val = args.__dict__.get(vo.dest)
                if val == vo.default:
                    continue
                if isinstance(val, (list, tuple)):
                    val = ' '.join(val)
                if vo.dest == 'limit':
                    settings['CLOSESPIDER_ITEMCOUNT'] = val
                    continue
                elif vo.dest == 'max':
                    settings['CONCURRENT_REQUESTS'] = val
                    continue
                elif vo.dest == 'dest':
                    settings['DESTRIBUT_RUN'] = val
                    continue
                elif vo.dest == 'proxy':
                    settings['USE_PROXY'] = val
                    continue
                argv.extend([opt, val])
            if args.url:
                argv.extend(['-a', 'START_URL=%s' % args.url])
            if args.start_index:
                argv.extend(['-a', 'START_INDEX=%s' % args.start_index])
            if args.end_index:
                argv.extend(['-a', 'END_INDEX=%s' % args.end_index])
        elif args.cmd == 'shell':
            argv = [sys.argv[0], args.cmd]
            if args.url:
                argv.append(args.url)
        elif args.cmd == 'view':
            if not args.url:
                print('please setting --url option')
                return None
            argv = [sys.argv[0], args.cmd, args.url]
        cmdline.execute(argv, settings)
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()