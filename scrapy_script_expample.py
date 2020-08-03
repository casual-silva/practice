# -*- coding: utf-8 -*-

__author__ = 'billy'

"""ti.com整站数据爬虫

requirements:
    scrapy>=1.2.0
    lxml
"""

import os
import re
import sys
import copy
import json
import random
import logging
import hashlib
import argparse
import requests
from Queue import Queue

# scrapy import
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.exceptions import DropItem, IgnoreRequest, CloseSpider, NotConfigured
# six
from six.moves.urllib.parse import urljoin
# lmxl
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
    'BOT_NAME': 'hqchipSpider',
    'ROBOTSTXT_OBEY': False,
    'COOKIES_ENABLED': True,
    'CONCURRENT_ITEMS': 1,
    'CONCURRENT_REQUESTS': 1,
    'DOWNLOAD_DELAY': 3,
    'DEFAULT_REQUEST_HEADERS': {
        'Accept': "text/html,application/xhtml+xml,application/json,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8",
        'Host': "www.ti.com.cn",
        'Referer': "https://www.ti.com.cn",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    },
    'DEFAULT_REQUESTS_COOKIES': {
        "userType": "Anonymous",
        "user_pref_language": "\"en-US\"",
        "tiSessionID": "0172a11b6f1b007e8d8aa5e861c003073003106b00bd0",
        "last-domain": "www.ti.com.cn",
        "ga_content_cookie": "%2Fanalog%20%26%20mixed-signal%2Fwireless%20connectivity%2Fsimplelink%20solutions%2Fsub-1%20ghz%20products%2Fcc1101-q1"
    },
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'DOWNLOADER_MIDDLEWARES': {
        __name__ + '.UniqueRequestMiddleware': 1,
        __name__ + '.ProxyRequestMiddleware': 3,
    },
    'ITEM_PIPELINES': {
        __name__ + '.MetaItemPipeline': 500,
    },
    'EXTENSIONS': {
        'scrapy.extensions.closespider.CloseSpider': 500,
    },
    'TELNETCONSOLE_ENABLED': False,
    'LOG_LEVEL': logging.DEBUG,
    'USE_PROXY': False

}

class UniqueRequestMiddleware(object):
    """去重请求中间件"""

    def __init__(self, crawler):
        name = 'spider_' + crawler.spider.name + '_item'
        self.mongo = hqchip.db.mongo[name]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def close_spider(self, spider):
        del self.mongo

    def process_request(self, request, spider):
        url = request.url
        key = hashlib.md5(url).hexdigest()
        info = self.mongo.find_one({'key': key})
        if info:
            logger.warn("ingore repeat url: %s" % request.url)
            raise IgnoreRequest("ingore repeat url: %s" % request.url)

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

class ProxyRequestMiddleware(object):
    """代理请求中间件"""

    def __init__(self):
        if not settings['USE_PROXY']:
            raise NotConfigured

    def process_request(self, request, spider):
        scheme, url, port = util.get_host(request.url)
        try:
            proxies = get_proxies(settings['USE_PROXY'])
        except:
            raise NotConfigured
        request.meta["proxy"] = proxies[scheme]

def get_proxies(proxies_type=1):
    '''
    返回指定代理 | 每次更新20个代理
    :param proxies_type: int 代理類型
    :return: proxies_dict
    '''
    if queue.qsize() > 0:
        return queue.get()
    if proxies_type == 1:
        proxies = util.get_abuyun_proxies()
        for i in range(20):
            queue.put(proxies)
    else:
        get_web_proxy()
    return queue.get()


def get_web_proxy():
    '''
    从指定接口获取代理ip
    :return:  代理数量, 代理列表
    '''
    logger.info('拨号代理中 ...')
    rs = requests.get(url='http://proxy.elecfans.net/proxys.php?key=AXw1KwWIsK&num=5&type=bohao')
    proxy = json.loads(rs.content)
    for vo in proxy['data'] * 4:
        proxies = {
            'https': 'http://%s' % (vo['ip'],),
            'http': 'http://%s' % (vo['ip'],),
        }
        queue.put(proxies)


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
    goods_other_name = scrapy.Field()


class MetaItemPipeline(object):
    """数据集管道"""

    def __init__(self, crawler):
        name = 'spider_' + crawler.spider.name + '_item'
        self.mongo = hqchip.db.mongo[name]
        self.mongo.ensure_index('key', unique=False)
        self.mongo.ensure_index('goods_sn', unique=True)

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
        data['key'] = hashlib.md5(data['url']).hexdigest()
        info = self.mongo.find_one({'goods_sn': data['goods_sn']})
        if not info:
            self.mongo.insert(data)
            logger.info('success insert mongodb : %s' % data['key'])
        else:
            self.mongo.update({'_id': info['_id']}, {"$set": data})
            logger.info('success update mongodb : %s' % data['key'])
        raise DropItem('success process')

    def close_spider(self, spider):
        del self.mongo


class HQChipSpider(CrawlSpider):
    """ti.com 蜘蛛"""
    name = 'ti'
    allowed_domains = ['www.ti.com.cn']
    start_urls = ['https://www.ti.com.cn/']
    base_url = 'https://www.ti.com.cn/'

    def __init__(self, name=None, **kwargs):
        self._init_args()
        super(HQChipSpider, self).__init__(name, **kwargs)

    def _init_args(self, **kwargs):
        self.headers = copy.deepcopy(settings['DEFAULT_REQUEST_HEADERS'])
        self.cookies = copy.deepcopy(settings['DEFAULT_REQUESTS_COOKIES'])
        pass

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        '''
        解析分类入口
        :param response:
        :return:
        '''
        sup_cats = response.xpath('//div[@class="columnGroup"]/div[@class="column"]')[:2]
        for sup_cat in sup_cats:
            sup_cat_urls = sup_cat.xpath('./ul/li/a/@href').extract()
            for sup_cat in sup_cat_urls[1:]:
                sup_cat = urljoin(self.base_url, sup_cat)
                yield Request(url=sup_cat, callback=self.get_cat_overview, headers=self.headers, cookies=self.cookies)

    def get_cat_overview(self, response):
        '''
        遍历分类请求产品列表
        :param response:
        :return:
        '''
        cat_level1s = response.xpath('//div[@class="pageContent"]//ul/li[@class="ti-nav-level1"]')
        for cat_level1 in cat_level1s:
            cat_level2s = cat_level1.xpath('.//li[@class="ti-nav-level2"]')
            if cat_level2s:
                for cat_level2 in cat_level2s:
                    cat_level3s = cat_level2.xpath('.//li[@class="ti-nav-level3"]')
                    if cat_level3s:
                        for cat_level3 in cat_level3s:
                            url = cat_level3.xpath('./a/@href').extract_first().replace('overview', 'products')
                            print 'GET： cat_level3: {0}'.format(url),'<'*100
                            yield Request(url=url, callback=self.parse_cat_resp, headers=self.headers, cookies=self.cookies)
                    else:
                        # 没有三级分类
                        url = cat_level2.xpath('./a/@href').extract_first().replace('overview', 'products')
                        print 'GET： cat_level2: {0}'.format(url), '<' * 100
                        yield Request(url=url, callback=self.parse_cat_resp, headers=self.headers, cookies=self.cookies)
            else:
                # 没有二级分类
                url = cat_level1.xpath('./a/@href').extract_first().replace('overview', 'products')
                print 'GET： cat_level1: {0}'.format(url), '<' * 100
                yield Request(url=url, callback=self.parse_cat_resp, headers=self.headers, cookies=self.cookies)

    def parse_cat_resp(self, response):
        '''请求产品列表页'''
        fid = response.xpath('//ti-selection-tool/@familyid').extract_first()
        family_url = 'http://www.ti.com.cn/selectiontool/paramdata/family/{0}/results?lang=cn&output=json'.format(fid)
        yield Request(url=family_url, callback=self.parse_api_models, headers=self.headers, cookies=self.cookies, dont_filter=True)

    def parse_api_models(self, response):
        '''请求产品型号接口'''
        json_data = json.loads(response.body)
        data_list = (item['o2'] for item in json_data['ParametricResults'])
        for model in data_list:
            product_detail_url = 'https://www.ti.com.cn/product/cn/{}'.format(model)
            yield Request(product_detail_url, callback=self.parse_model_detail, headers=self.headers, cookies=self.cookies)

    def parse_model_detail(self, response):
        '''解析产品详情'''
        json_html = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.body, re.S)
        if not json_html:
            raise DropItem('匹配源码内容异常 请检查：{0}'.format(response.url))
        json_data = json.loads(json_html[0])
        product_list = json_data['offers']
        pre_url = 'https://www.ti.com.cn/product/cn/{}'.format(json_data['mpn'])
        description = json_data['description']
        doc_url = urljoin(self.base_url, response.xpath('//div/a[@data-navtitle="data sheet"]/@href').extract_first())
        attrs_items = response.xpath('//ti-multicolumn-list/ti-multicolumn-list-row')
        attr_list = []
        # 获取属性列表
        for attrs_item in attrs_items:
            attr = attrs_item.xpath('./ti-multicolumn-list-cell/span/text()').extract()
            if not attr:
                continue
            key = util.cleartext(attr[0])
            val = util.cleartext(attr[1])
            if key and val:
                attr_list.append((key, val))
        # 获取分类列表
        cat_list = []
        cat_items = response.xpath('//ti-breadcrumb/ti-breadcrumb-section/a')[1:]
        for cat_item in cat_items:
            ckey = util.cleartext(cat_item.xpath('./text()').extract_first())
            cval = urljoin(self.base_url, cat_item.xpath('./@href').extract_first())
            cat_list.append((ckey, cval))

        for data in product_list:
            item = GoodsItem()
            data = data['itemOffered']
            item['url'] = pre_url
            item['goods_sn'] = data['sku']
            item['goods_other_name'] = item['goods_name'] = data['mpn']
            item['provider_name'] = data['brand']
            item['provider_url'] = ''
            item['goods_desc'] = description
            item['goods_img'] = item['goods_thumb'] = ''
            item['doc'] = doc_url
            item['rohs'] = 0
            shop_price = data['offers'].get('price')
            item['tiered'] = []
            if not shop_price:
                item['stock'] = [0, 1]  # 库存
                item['increment'] = 1
            else:
                # 庫存判斷
                if not data['offers'].get('inventoryLevel'):
                    item['stock'] = [0, 1]
                else:
                    item['stock'] = [util.intval(data['offers']['inventoryLevel']), 1]  # 库存
                for price_item in data['offers']['priceSpecification']:
                    pnum = price_item['eligibleQuantity']['minValue']
                    pval = price_item['price']
                    item['tiered'].append((util.intval(pnum), util.floatval(pval)))
                item['increment'] = item['tiered'][0][0]
            if not item['tiered']:
                item['tiered'] = [[0, 0.00]]
            # 属性
            item['attr'] = attr_list
            # 分类
            item['catlog'] = cat_list
            yield item

    @property
    def closed(self):
        """蜘蛛关闭清理操作"""

        def wrap(reason):
            # del self.queue
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
    run_group.add_argument('-p', '--proxy', help='使用代理进行请求0: 不使用代理 | 1: 阿布云代理 | 2: 拨号代理',
                           dest='proxy', default=0, type=int)
    run_group.add_argument("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                           help="设置爬虫参数（可以重复）")
    run_group.add_argument("-o", "--output", metavar="FILE",
                           help="输出 items 结果集 值FILE (使用 -o 将定向至 stdout)")
    run_group.add_argument("-t", "--output-format", metavar="FORMAT",
                           help="基于 -o 选项，使用指定格式输出 items")
    run_group.add_argument('-d', '--dist', help='分布式运行，用于其他进程提交数据',
                           action='store_true', default=False)
    gen_group = parser.add_argument_group(title='通用选择项')
    gen_group.add_argument('-u', '--url', help='设置URL，运行操作设置该项则为起始爬取URL，\
                                                                    调试操作设置则为调试URL，查看操作则为打开查看URL')
    args = parser.parse_args()
    # args.cmd = 'runspider'
    if args.help:
        parser.print_help()
    elif args.cmd:
        settings = Settings(settings)
        if args.cmd == 'runspider':
            argv = [sys.argv[0], args.cmd, sys.argv[0]]
            for vo in run_group._group_actions:
                opt = vo.option_strings[0]
                val = args.__dict__.get(vo.dest)
                # if val == vo.default:
                #     continue
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
                    print val,5161
                    continue
                # argv.extend([opt, val])
            if args.url:
                argv.extend(['-a', 'START_URL=%s' % args.url])
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
