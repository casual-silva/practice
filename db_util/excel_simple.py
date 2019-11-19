#!/usr/bin/env python
# -*- coding: utf-8 -*-

reload(sys)
sys.setdefaultencoding('utf8')
# 此处使用的是本地测试数据库
db_config = config.DATABASES['mysql'][0].copy()
# db_config = config.DATABASES['localhost'].copy()
db_config['data_type'] = 'tuple'
db_config['db'] = 'oneyac'
db_config['tablepre'] = 'ic_'

# 修改日志配置
LOGDIR = config.LOGDIR
_handler = config.RotatingFileHandler(filename = os.path.join(LOGDIR, 'spider_' + datetime.datetime.now().strftime("%Y-%m-%d_%H") + '_oneyac' + ".log"), mode = 'a+')
_handler.setFormatter(logging.Formatter(fmt = '>>> %(asctime)-10s %(name)-12s %(levelname)-8s %(message)s',datefmt ='%H:%M:%S'))
_logger = logging.getLogger('hqchip_spider_oneyac')
_logger.addHandler(_handler)
# 在控制台打印
_console = logging.StreamHandler()
_logger.addHandler(_console)


# queue
mq = RabbitMQ()
dqueue_ = Queue()

ip_list = []
start_time = time.time()
# 第一次请求标记
first_enter_flag = True
# 代理过期时间: 秒, 默认5 min
ip_expire_time = 60*5
# 代理接口
api_proxy = 'http://proxy.elecfans.net/proxys.php?key=AXw1KwWIsK&num=5&type=bohao'
# api_proxy = 'http://proxy.elecfans.net/proxys.php?key=nTAZhs5QxjCNwiZ6&num=10&type=pay'

class Aneyac(DbSession):
    def __getattr__(self, attr):
        tname = threading.current_thread().name
        if tname not in self.thread_queue:
            self.thread_queue[tname] = db_mysql(**db_config)
        return getattr(self.thread_queue[tname], attr)


_headers = {'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Upgrade-Insecure-Requests': '1',
            # 'Host': 'www.oneyac.com',
            'Cookie': 'SESSION=NDVhODdlZmYtNTk3YS00MDQyLWE2ZDgtMWE4ODI2YWU1Nzg1; Hm_lvt_2d41db31b18b75206ed7c59c33f5c313=1563851690; coupon_dialog_cookie=hide; Hm_lpvt_2d41db31b18b75206ed7c59c33f5c313=1563854329',
            'Referer': 'http://www.oneyac.com/search.html?keyword=BAT760-7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            # 'Proxy-Connection': 'keep-alive'
            }

def get_time_desc(t):
    '''
    获取时间描述
    :param t:
    :return:
    '''
    _time_desc = ''
    h = int(t / 3600)
    if h >= 1:
        _time_desc += '%s 小时' % h
    m = int((t - h * 3600) / 60)
    if m >= 1:
        _time_desc += '%s 分' % m
    s = util.number_format(t - h * 3600 - m * 60, 3)
    if s >= 0:
        _time_desc += '%s 秒' % s
    return _time_desc


def str_to_unicode(text):
    """字符串转unicode字符串"""
    if not isinstance(text, str):
        return text
    return text.decode('utf-8')


class IcSpider(object):
    """唯样商城数据采集"""

    def __init__(self, **kwargs):
        self._init_args(**kwargs)
        if self._clear:
            self.clear_data()
            if not self._action:
                return
        if not self._action:
            self._action = 'catalog'
        if self._action == 'export':
            self.export_excel()
        if self.simple:
            self.fetch_simple_goods()
            return
        if self._action == 'catalog':
            self._try_cnt = 0
            while 1:
                if self.fetch_catalog() > 0:
                    break
            print '产品分类采集完毕'
            self._action = 'page'
        if self._action == 'page':
            self.parse_catalog()
        self.flush_save()
        _run_time = time.time() - self._start_time
        print '=' * 50
        print '操作完毕, 共获取: {0}条数据, 耗时：{1}'.format(self.numbers, get_time_desc(_run_time))
        print '记录的异常数为:{0}, 若异常数量大请检查日志.'.format(self.abnormal)

    def _init_args(self, **kwargs):
        """初始化参数"""
        self._start_time = time.time()
        self.__del = set()
        self.__mysql = None
        self.queue = mq
        self.use_proxy = kwargs.get('use_proxy', False)
        self._action = kwargs.get('action')
        self._clear = kwargs.get('clear', False)
        self.max_threads = kwargs.get('threads', '3')
        if self.use_proxy:
            self.useproxy()
        self._interval = kwargs.get('interval', 0.5)
        self._cache = {}
        self._dpool = dqueue_
        self.abnormal = 0
        self.numbers = 0
        self.catid = kwargs.get('catid')
        if self.catid:
            self.catid = self.catid.split(',')
        self.simple = kwargs.get('simple', '')
        self.filter = kwargs.get('filter', False)
        self.syn = kwargs.get('syn', False)


    @property
    def mysql(self):
        """连接mysql"""
        self.__mysql = Aneyac()
        return self.__mysql

    def fetch_catalog(self):
        """获取分类"""
        # 如果存在数据证明初始化了，无需再次操作
        if self.mysql.count('category') > 0:
            return 1
        if self._try_cnt > 5:
            raise Exception('重试超过5次')
        url = 'http://www.oneyac.com/search/product_category.html'
        try:
            proxies = self.get_proxies(use_proxy=self.use_proxy)
            _headers['referer'] = url
            rs = requests.get(url, headers=_headers, timeout=30, proxies=proxies, verify=False)
        except Exception as e:
            print '数据请求异常：%s' % e
            print '正在进行重试...'
            self._try_cnt += 1
            return 0

        if rs.status_code != 200:
            print '请求错误，网页响应码:%s' % rs.status_code
            if self.use_proxy:
                print '使用的代理为：%s' % proxies
            print '正在进行重试...'
            self._try_cnt += 1
            return 0
        rs.encoding = 'utf-8'
        root = etree.HTML(rs.content, parser=etree.HTMLParser(encoding='utf-8'))
        if root is None:
            self._try_cnt += 1
            return 0
        print('数据获取成功')
        catList = []
        levelListAll = root.xpath('//div[@class="category wraper"]//div[@class="c-catgBar-pg"]')
        _rep = re.compile(r'(.+).*?\(([\d,]+)\)')
        for levelList in levelListAll:
            cat1 = levelList.xpath('./h1')
            if not cat1:
                print '没有目录'
                continue
            cat_name = self.totext(cat1[0])
            # 获取二级分类
            list2 = []
            try:
                cat2List = levelList.xpath('./ul/li/a')
            except:
                cat2List = []
            for cat2 in cat2List:
                goods_count = 0
                name = cat2.attrib['title']
                match = _rep.search(name)
                if match:
                    name = match.group(1)
                    goods_count = int(match.group(2).replace(',', ''))
                url = urlparse.urljoin('http://www.oneyac.com/', cat2.attrib['href'])
                categoryId = util.intval(url)
                list2.append({
                    'name': util.cleartext(name),
                    'url': url,
                    'count': goods_count,
                    'categoryId': categoryId,
                })
            goods_count = 0
            match = _rep.search(cat_name)
            cat1_url = ''
            if match:
                cat_name = match.group(1)
                goods_count = int(match.group(2).replace(',', ''))
                cat1_url = util.urljoin(url, levelList.xpath('./h1/a/@href')[0])
            catList.append({
                'name': util.cleartext(cat_name),
                'url': cat1_url,
                'list': list2,
                'count': goods_count
            })

        if not catList:
            print '产品目录数据获取异常'
            self._try_cnt += 1
            return 0

        print '正在保存分类数据'
        for cat in catList:
            islast = 0 if 'list' in cat and cat['list'] else 1
            cat_id = self.mysql.insert('category', data={
                'cat_name': cat['name'],
                'url': cat['url'],
                'parent_id': 0,
                'islast': islast,
                'goods_count': cat['count'],
                'level': 1,
            }, return_insert_id=1)
            if not islast:
                for cat2 in cat['list']:
                    islast = 0 if cat2.has_key('list') and cat2['list'] else 1
                    self.mysql.insert('category', data={
                        'cat_name': cat2['name'],
                        'url': cat2['url'],
                        'parent_id': cat_id,
                        'islast': islast,
                        'goods_count': cat2['count'],
                        'level': 2,
                        'categoryId': cat2['categoryId'],
                    })
        print '保存分类成功'
        del catList
        return 1

    def parse_catalog(self):
        """获取产品分类链接，并获取分类所有商品详情"""
        if self.catid:
            catids = [int(i) for i in self.catid]
            id_ranges = ['in', catids] if len(catids) > 1 else  catids[0]
            condition = {'level': 2, 'goods_count': ['>', 0], 'categoryId': id_ranges}
            res = self.mysql.select('category', condition=condition, fields=('cat_id', 'url', 'cat_name', 'goods_count'))
            print '采集指定目录: {0}'.format(res)
        else:
            res = self.mysql.select('category', condition={'level': 2, 'goods_count': ['>', 0]},
                                fields=('cat_id', 'url', 'cat_name', 'goods_count'))
        if not res:
            return 1
        task_list = []
        # self.max_threads = 1
        for row in res:
            print '*'*100
            kwargs = {
                'cat_id': row[0],
                'cat_name': row[2],
                'goods_count': row[3],
            }
            catalog_url = row[1]
            # task = multiprocessing.Process(target=self.parse_pages, args=(catalog_url,), kwargs=kwargs, name="thread_{0}".format(len(task_list)))
            task = threading.Thread(target=self.parse_pages, args=(catalog_url,), kwargs=kwargs,
                                    name="thread_{0}".format(len(task_list)))
            task.start()
            task_list.append(task)
            if len(task_list) >= self.max_threads:
                for task in task_list:
                    task.join()
                self.flush_save()
                task_list = []
        # self.flush_save()
    #
    def parse_pages(self, url, retry=0, **kwargs):
        """获取分页数据"""
        if 'cat_name' in kwargs:
            print('正在获取分类 %s 下的分页数据，URL: %s cat_id: %s' % (kwargs['cat_name'].encode('utf-8'), url.encode('utf-8'), kwargs['cat_id']))
        # 获取目录id
        catalog_id = re.search(r'categoryId=(\d+)', url)
        if not catalog_id:
            print('无法从分类URL中解析分类ID {0}'.format(url))
            return 0
        catalog_id = catalog_id.group(1)
        try:
            proxies = self.get_proxies(use_proxy=self.use_proxy)
            _headers['referer'] = url
            rs = requests.get(url, headers=_headers, timeout=30, proxies=proxies, verify=False)
        except Exception as e:
            if retry <= 3:
                retry += 1
                print 'cat_id:{0} 正在进行第{1}次重试...url: {2}'.format(kwargs['cat_id'], retry, url)
                return self.parse_pages(url, retry=retry, **kwargs)
            else:
                self.abnormal += 1
                print 'cat_id:{0} 请求分类失败 error: {1}'.format(kwargs['cat_id'], e)
                return 0
        data_str_match = re.findall(r'LIST_FORM = (\{.*?\};)', rs.content, re.S)
        # 获取字典数据
        try:
            data_str_match = re.findall(r'(\{.*?\""),.*?getSearchToken\("1", "(.*?)"\)', data_str_match[0], re.S)
        except:
            self.abnormal += 1
            print '正则匹配表单数据异常, url:{0}, response.content:{1}'.format(url, rs.content)
        data_dict = json.loads(data_str_match[0][0] + '}')
        token = data_str_match[0][1]
        # 加密参数
        token = "on@hol11{0}!xm@{1}1wyno{2}eyac$der".format(token[22:33], token[33:], token[:22])
        data_dict['token'] = token
        data_dict['sort'] = 'desc'
        data_dict['pageSize'] = 100
        data_dict['orderBy'] = 'inventory'
        #暂时没有agg_attr_name_filters[] 属性
        parse_data = {
            'callback': "jQuery_data",
            'paramsDTO': json.dumps(data_dict),
            '_': str(int(time.time() * 1000))
        }
        #请求接口数据:
        api_url = 'http://soic.oneyac.com/search.html'
        #获取分页数据
        page = 0
        while 1:
            try:
                print '获取cat_id: {0} 第{1}页'.format(kwargs['cat_id'], page + 1)
                rs_ = requests.get(url=api_url, params=parse_data, headers=_headers, proxies=proxies, timeout=30)
            except:
                proxies = self.get_proxies(use_proxy=self.use_proxy)
                try:
                    rs_ = requests.get(url=api_url, params=parse_data, headers=_headers, proxies=proxies, timeout=30)
                except Exception as e:
                    print '获取cat_id: {0} 第{1}页 失败! error: {2}'.format(kwargs['cat_id'], page + 1, e)
                    break
            #解析获取到的json数据,并保存数据
            try:
                is_last, next_token = self.parse_detail(rs_.content, retry=0, **kwargs)
            except Exception as e:
                self.abnormal += 1
                print '解析详情数据异常{0}'.format(e)
                print rs_.content
                break
            if is_last:
                print 'cat_id: {0} is_last: True'.format(kwargs['cat_id'])
                self.flush_save()
                break
            #修改parse_data参数, 请求下一页
            page += 1
            if not page % 10:
                self.flush_save()
            data_dict['page'] = str(page)
            data_dict['token'] = "on@hol11{0}!xm@{1}1wyno{2}eyac$der".format(next_token[22:33], next_token[33:], next_token[:22])
            parse_data['paramsDTO'] = json.dumps(data_dict)
            parse_data['_'] = int(time.time() * 1000)
            time.sleep(self._interval)
        time.sleep(self._interval)

    def fetch_simple_goods(self, retry=1):
        url = 'http://www.oneyac.com/search.html?keyword={0}'.format(self.simple)
        req = requests.session()
        try:
            proxies = self.get_proxies(use_proxy=self.use_proxy)
            _headers['referer'] = url
            print '获取{0}数据数据中...'.format(self.simple)
            rs = req.get(url, headers=_headers, timeout=30, proxies=proxies, verify=False)
        except Exception as e:
            if retry <= 3:
                retry += 1
                print 'goods_name:{0} 正在进行第{1}次重试...url: {2}'.format(self.simple, retry, url)
                return self.fetch_simple_goods(retry=retry)
            else:
                self.abnormal += 1
                print 'goods_name:{0} 请求数据失败 error: {1}'.format(self.simple, e)
                return 0
        # 获取字典数据
        try:
            data_str_match = re.findall(r'.*?getSearchToken\("1","(.*?)"\).*?', rs.content, re.S)
        except:
            self.abnormal += 1
            print '正则匹配表单数据异常, url:{0}, response.content:{1}'.format(url, rs.content)
            return
        token = data_str_match[0]
        # 加密参数
        token = "on@hol11{0}!xm@{1}1wyno{2}eyac$der".format(token[22:33], token[33:], token[:22])
        data_dict = {"page":0,
                     "brandId":"",
                     "keyword": self.simple,
                     "token": token,
                     "supplierId":"1",
                     "sort":"desc",
                     "orderBy":"inventory",
                     "isNeedAggregation": True,
                     "pageSize":10
                     }
        parse_data = {
            'callback': "jQuery_data",
            'paramsDTO': json.dumps(data_dict),
            '_': str(int(time.time() * 1000))
        }
        # 请求接口数据:
        api_url = 'http://soic.oneyac.com/search.html'
        try:
            print '请求接口详情数据中'
            rs_ = req.get(url=api_url, params=parse_data, headers=_headers, proxies=None, timeout=30)
        except:
            try:
                rs_ = req.get(url=api_url, params=parse_data, headers=_headers, proxies=None, timeout=30)
            except Exception as e:
                print 'goods_name: {0} 失败! error: {1}'.format(self.simple, e)
                return
        # 解析获取到的json数据,并保存数据
        try:
            self.parse_detail(rs_.content, retry=0)
        except Exception as e:
            self.abnormal += 1
            print '解析详情数据异常, response.content:{0}, {1}'.format(rs_.content, e)
            return
        self.flush_save()

    def parse_detail(self, data, retry=0, next_token=None, **kwargs):
        """获取并解析json数据"""
        json_rep = re.findall(r'jQuery_data\((.*?})\)', data, re.S)
        json_dict = json.loads(json_rep[0])
        next_token = json_dict.get('token')
        is_last = json_dict['page']['last']
        content_list = json_dict['page']['content']
        # 遍历每一个产品
        print len(content_list)
        for content in content_list:
            data = {}
            if not content or not isinstance(content, dict):
                print '解析异常, content_list: {0}'.format(content_list)
                self.abnormal += 1
                raise StopIteration
            #先判断库存
            data['stock'] = content['inventory']
            data['cat_id'] = kwargs.get('cat_id', 0)
            if data['stock'] == 0:
                print 'cat_id: {0} 获取到无库存数据,结束当前数据获取! content_list_len: {1}'.format(data['cat_id'], len(content_list))
                return True, next_token
            data['increment'] = content['orderStepNum']
            data['min_buynum'] = content['orderMinNum']
            data['min_unit_str'] = ''
            data['min_unit'] = ''
            data['extension_code'] = ''
            data['tiered'] = []
            try:
                price_model_list = content['priceModelList']
                if price_model_list:
                    for price_item in content['priceModelList']:
                        data['tiered'].append([
                            util.intval(price_item['stepNum']),
                            util.floatval(price_item['price'])
                        ])
                if not data['tiered']:
                    data['tiered'] = [[0, 0.00]]
            except Exception as e:
                print e, data['tiered']
            data['shop_price'] = data['tiered'][-1][1]
            data['shop_price'] = util.floatval(data['shop_price'])
            data['sale_count'] = 0
            data['sale_unit'] = ''
            data['seller_note'] = ''
            data['goods_img'] = content['logoUrl']
            data['goods_thumb'] = ''
            data['goods_sn'] = content['id']
            data['goods_desc'] = content.get('mfrsInfoDesc', '')
            data['package'] = ''
            data['goods_name'] = content['name']
            data['goods_name_style'] = content['stkCode'] if content['stkCode'] else data['goods_name']
            data['brand_name'] = content['brandName']
            brand_id = content['brandId']
            data['brand_url'] = 'http://www.oneyac.com/brand/{0}.html'.format(brand_id)
            data['brand_logo'] = content.get('supplierLogoUrl', '')
            data['url'] = 'http://www.oneyac.com/product/{0}.html'.format(data['goods_sn'])
            self._dpool.put(data)
            self.numbers += 1
        # self.flush_save()
        return is_last, next_token

    def flush_save(self):
        """缓冲区数据保存"""
        if self.syn:
            put_oneyac_list = []
            while self._dpool.qsize():
                data = self._dpool.get()
                put_oneyac_list.append(data)
            print '异步更新暂不可用'
            sys.exit()
            # self.queue.put_queue_list(message_list=put_oneyac_list, queue_name='site_data_oneyac')
        else:
            task2_list = []
            while self._dpool.qsize():
                data = self._dpool.get()
                # task2 = multiprocessing.Process(target=self.save_data, args=(data,),
                #                         name="thread_t2_{0}".format(len(task2_list)))
                task2 = threading.Thread(target=self.save_data, args=(data,),
                                        name="thread_t2_{0}".format(len(task2_list)))
                task2.start()
                task2_list.append(task2)
                if len(task2_list) >= 8:
                    for task2 in task2_list:
                        task2.join()
                    task2_list = []


    def save_data(self, data):
        """保存数据"""
        if not data:
            return None
        brand_id = 0
        brand_name = data.get('brand_name', '')
        if not self.filter:
            if data['stock'] == 0 or data['min_buynum'] > data['stock'] or data['tiered'][0][1] == 0:
                print '{0} 不可上架数据 已丢弃'.format(data['goods_name'])
                return None
        if brand_name:
            res = self.mysql.select('brand', fields='brand_id', condition={'brand_name': brand_name}, limit=1)
            if res:
                brand_id = res[0]
            else:
                try:
                    brand_id = self.mysql.insert('brand', data={
                        'brand_name': brand_name,
                        'site_url': data.get('brand_url', ''),
                        'digikey': data.get('brand_url', ''),
                        'brand_logo': data.get('brand_logo',''),
                        'first_letter': '',
                        'goods_count': 0,
                        'brand_desc': '',
                    }, return_insert_id=1)
                except Exception as e:
                    brand_id = 0
                    if 'Duplicate entry' in str(e):
                        res = self.mysql.select('brand', fields='brand_id',
                                                condition={'brand_name': brand_name}, limit=1)
                        if res:
                            brand_id = res[0]
                    else:
                        _logger.error('保存品牌异常')

        goods_data = {
            'cat_id': data.get('cat_id', 0),
            'goods_sn': data['goods_sn'],
            'goods_name': data['goods_name'].upper(),
            'goods_name_style': data.get('goods_name_style', ''),
            'brand_id': brand_id,
            'provider_name': brand_name,
            'doc_url': '',
            'goods_number': data['stock'],
            'min_buynum': data['min_buynum'],
            'goods_thumb': data.get('goods_thumb', ''),
            'goods_img': data.get('goods_img', ''),
            'original_img': data.get('goods_img', ''),
            'is_real': 1,
            'suppliers_id': brand_id,
            'is_check': 0,
            'digikey_url': data['url'],
            'series': data.get('series', ''),
            'source_type': 0,
            'shop_price': data['shop_price'],
            'increment': data.get('increment', 1),
            'style': '',
            'seller_note': data.get('seller_note', ''),
            'sale_unit': data['sale_unit'],
            'sale_count': 0,
            'min_unit_str': data['min_unit_str'],
            'min_unit': data['min_unit'],
            'package': data['package'],
            'goods_desc': data.get('goods_desc', ''),
            'extension_code': data.get('extension_code', ''),
            'add_time': int(time.time()),
            'sale_amount': 0.0000
        }
        is_update = False
        goods_id = 0
        try:
            goods_id = self.mysql.insert('goods', data=goods_data, return_insert_id=1)
            print '型号 %s 数据保存至ic_goods库成功!' % util.unicode_to_str(goods_data['goods_name'])
        except Exception as e:
            if 'Duplicate entry' in str(e):
                is_update = True
                self.mysql.update('goods', condition={'goods_sn': goods_data['goods_sn']}, data=goods_data)
                print '型号 %s 数据更新至ic_goods库成功!' % util.unicode_to_str(goods_data['goods_name'])
                # return 603
            elif 'Warning' in str(e):
                config.LOG.debug('STATUS:607 ; INFO:%s ' % util.traceback_info(e))
            else:
                config.LOG.exception('STATUS:-607 ; INFO:%s ; DATA:%s' % (util.traceback_info(e), data))
                return -607
        if not goods_id:
            info = self.mysql.select('goods', fields='goods_id', condition={'goods_sn': goods_data['goods_sn']},
                                     limit=1)
            goods_id = info[0]
        table_id = int(goods_id) % 10
        # 保存价格
        # return 0
        price_list = []
        for val in data['tiered']:
            price_list.append({
                "purchases": val[0],
                "price": val[1],
            })
        # 获取价格信息
        ptable = 'goods_price_%s' % table_id
        # pdata  = self.mysql.select(ptable, condition={'goods_id': goods_id}, limit=1, fields='goods_id,price')
        if is_update:
            self.mysql.update(ptable, condition={'goods_id': goods_id},
                              data={'price': json.dumps(price_list)})
            print '型号 %s 数据更新至goods_price成功!' % util.unicode_to_str(goods_data['goods_name'])
        else:
            self.mysql.insert(ptable, data={'goods_id': goods_id, 'price': json.dumps(price_list)})
            print '型号 %s 数据保存至goods_price成功!' % util.unicode_to_str(data['goods_name'])
        return goods_id

    def get_hqchip_self_goods(self, name):
        """获取自营产品信息"""
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        print('获取自营产品: {0}'.format(name))
        condition = {'goods_name': name}
        dgk_goods = db.hqchip.select('goods', fields='goods_id,goods_no,cat_id,provider_name',
                                     condition=condition, limit=1)
        if not dgk_goods:
            return {
                'goods_no': '',
                'cat_id': 0,
                'goods_id': 0,
                'provider_name': '',

            }
        return dgk_goods

    def clear_data(self):
        """清空数据"""
        clear_all = 1
        action = None
        if not action:
            action = 'catalog'

        if action == 'catalog':
            print('正在清空 ic_category 的数据...')
            try:

                self.mysql.execute('TRUNCATE  TABLE `ic_category`;')
                print('成功清空 ic_category 的数据...')
            except Exception, e:
                print e
                return 0
            if clear_all:
                action = 'page'

        if action == 'page':
            print '正在清空 ic_page 和 ic_url 的数据...'
            try:
                self.mysql.execute('TRUNCATE  TABLE `ic_page`;')
                self.mysql.execute('TRUNCATE  TABLE `ic_url`;')
                print('成功清空 ic_page 和 ic_url 的数据...')
            except Exception, e:
                print e
                return 0
            # if clear_all:
            #     action = 'data'

        if action == 'data':
            print '正在清空 ic_brand 、ic_goods 及 ic_goods_price_* 的数据...'
            try:
                self.mysql.execute('TRUNCATE  TABLE `ic_brand`;')
                self.mysql.execute('TRUNCATE  TABLE `ic_goods`;')
                self.mysql.execute('ALTER TABLE `ic_goods` AUTO_INCREMENT = 3600000001;')
                for i in range(10):
                    self.mysql.execute('TRUNCATE  TABLE `ic_goods_price_%s`;' % i)
                print('成功清空 ic_brand 、ic_goods 及 ic_goods_price_* 的数据...')
            except Exception, e:
                print e
                return 0
    # get_prolist
    def get_proxies(self, use_proxy=None, proxies=None, use_expire_time=True):
        '''
        :param use_proxy: 是否使用代理标识
        :param proxies:
        :param use_expire_time: example >> False 每次都请求代理接口更新代理
        :return: proxies
        '''
        if use_proxy:
            proxy = self.useproxy(use_expire_time=use_expire_time)
            if proxy:
                proxies = {
                    'https': 'http://%s' % (proxy,),
                    'http': 'http://%s' % (proxy,),
                }
        return proxies

    def useproxy(self, use_expire_time=True, **kwargs):
        global start_time, first_enter_flag
        if first_enter_flag:
            try:
                proxy = self.get_web_proxy()
            except Exception as e:
                print '获取代理出错: {0}'.format(e)
                return None
            first_enter_flag = False
            return proxy
        else:
            expire_time = int(time.time() - start_time)
            if (use_expire_time and expire_time >= ip_expire_time):
                # 超出过期时间, 更新全局ip_list并随机取一个ip
                try:
                    start_time = time.time()
                    proxy = self.get_web_proxy()
                except Exception as e:
                    print '获取代理出错: {0}'.format(e)
                    return None
            elif not use_expire_time:
                try:
                    proxy = self.get_web_proxy()
                except Exception as e:
                    print '获取代理出错: {0}'.format(e)
                    return None
            else:
                # 过期时间内,从全局ip_list中随机取一个ip
                proxy = random.choice(ip_list)
            return proxy

    def get_web_proxy(self):
        '''
        从指定接口获取代理ip
        :return:  代理数量, 代理列表
        '''
        print '请求代理中 ...'
        rs = requests.get(url=api_proxy, timeout=10)
        data = json.loads(rs.content)
        if not data['data']:
            print '请求过快 重新请求中 ...'
            time.sleep(0.1)
            return self.get_web_proxy()
        global ip_list
        ip_list = []
        for item_ip in data['data']:
            ip_list.append(item_ip['ip'])
        return random.choice(ip_list)

    def _get_categry(self, cat_id):
        """获取指定分类"""
        if not cat_id:
            return None
        if cat_id in self._cache:
            return self._cache[cat_id]
        info = db.hqchip.select('dgk_category', condition={'cat_id': cat_id}, fields='cat_id,cat_name,parent_id',
                                limit=1)
        if not info:
            self._cache[cat_id] = None
        else:
            info['cat_name'] = info['cat_name'].replace('|', '')
            self._cache[cat_id] = info
        return self._cache[cat_id]

    def _get_categry_list(self, cat_id):
        """获取指定分类所有分类列表"""
        if not cat_id:
            return None
        cats = []
        cnt = 0
        limit = 5
        while 1:
            info = self._get_categry(cat_id)
            if not info:
                break
            cats.insert(0, info['cat_name'])
            if info['parent_id'] <= 0:
                break
            cat_id = info['parent_id']
            cnt += 1
            if cnt >= limit:
                break
        return cats

    def export_excel(self):
        """导出Excel"""
        import xlsxwriter
        filename = os.path.join(config.APP_ROOT, 'database', 'export', 'Anyac.xlsx')
        _fpath = os.path.dirname(filename)
        if not os.path.isdir(_fpath):
            os.makedirs(_fpath)
        wb = xlsxwriter.Workbook(filename)
        ws = wb.add_worksheet(u'唯样商城')
        merge_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12, 'font': u'宋体'})
        format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'size': 9, 'font': u'宋体', 'border': 1})
        format2 = wb.add_format({'align': 'left', 'valign': 'vcenter', 'size': 9, 'font': u'宋体', 'border': 1})
        cat_list = self.mysql.select('category', condition={'level': 2}, fields=('cat_id', 'cat_name'))
        i = 0
        ws.set_row(i, 30)
        ws.set_column(0, 0, 40)
        ws.set_column(1, 1, 30)
        ws.set_column(2, 7, 20)
        ws.set_column(8, 8, 10)
        ws.set_column(9, 9, 20)
        ws.set_column(10, 10, 10)
        ws.set_column(11, 12, 20)
        ws.set_column(13, 13, 50)
        ws.set_column(14, 17, 10)
        ws.set_column(18, 18, 50)
        ws.set_column(19, 19, 50)
        ws.merge_range(i, 0, i, 19, u'唯样商城产品数据', merge_format)
        i += 1
        ws.write(i, 0, u'产品名称', format)
        ws.write(i, 1, u'厂家型号', format)
        ws.write(i, 2, u'品牌', format)
        ws.write(i, 3, u'封装', format)
        ws.write(i, 4, u'最小包装', format)
        ws.write(i, 5, u'一级分类', format)
        ws.write(i, 6, u'二级分类', format)
        ws.write(i, 7, u'库存数量', format)
        ws.write(i, 8, u'库存单位', format)
        ws.write(i, 9, u'销售数量', format)
        ws.write(i, 10, u'销售单位', format)
        ws.write(i, 11, u'最低价格', format)
        ws.write(i, 12, u'最低销售总额', format)
        ws.write(i, 13, u'描述', format)
        ws.write(i, 14, u'唯样编号', format)
        ws.write(i, 15, u'自营编号', format)
        ws.write(i, 16, u'自营品牌', format)
        ws.write(i, 17, u'自营分类ID', format)
        ws.write(i, 18, u'自营分类', format)
        ws.write(i, 19, u'更新时间', format)
        for cat in cat_list:
            # 获取分类下的产品数据
            goods_list = self.mysql.query("""
                SELECT t3.cat_name AS parent_cat_name,t2.cat_name,t4.brand_name,t1.goods_name,
                t1.goods_name_style,t1.package,t1.sale_count,t1.shop_price,t1.min_unit_str,t1.goods_number,
                t1.goods_desc,t1.min_unit,t1.sale_unit,t1.goods_sn,t1.add_time FROM ic_goods AS t1 LEFT 
                JOIN ic_category AS t2 ON t1.cat_id = t2.cat_id
                LEFT JOIN ic_category AS t3 ON t2.parent_id = t3.cat_id LEFT JOIN ic_brand AS t4 
                ON t1.`brand_id` = t4.`brand_id` WHERE t1.cat_id = %s ORDER BY t1.sale_count DESC;
            """, (cat[0],))

            for row in goods_list:
                i += 1
                _unit = None
                try:
                    min_unit_list = row[8].encode('utf-8').split(',')
                    if min_unit_list[0]:
                        _min_unit = util.number_format(min_unit_list[2], 0)
                    else:
                        _min_unit = 1
                    if _min_unit <= 0:
                        _min_unit = 1
                    _unit = min_unit_list[0]
                except:
                    _min_unit = 1
                if not _unit:
                    _unit = row[11]
                _sale_unit = row[12].encode('utf-8')
                if '多' in _sale_unit:
                    _sale_unit = _sale_unit.replace('多', '')
                ws.write(i, 0, str_to_unicode(row[3]), format2)
                ws.write(i, 1, str_to_unicode(row[4]), format2)
                ws.write(i, 2, str_to_unicode(row[2]), format)
                ws.write(i, 3, str_to_unicode(row[5]), format)
                ws.write(i, 4, _min_unit, format)
                ws.write(i, 5, str_to_unicode(row[0]), format2)
                ws.write(i, 6, str_to_unicode(row[1]), format2)
                ws.write(i, 7, str_to_unicode(row[9]), format)
                ws.write(i, 8, str_to_unicode(_unit), format)
                ws.write(i, 9, str_to_unicode(row[6]), format)
                ws.write(i, 10, str_to_unicode(_sale_unit), format)
                ws.write(i, 11, str_to_unicode(row[7]), format)
                ws.write(i, 12, int(row[6]) * float(row[7]), format)
                ws.write(i, 13, str_to_unicode(row[10]), format2)
                goods = self.get_hqchip_self_goods(row[4])
                ws.write(i, 14, row[13], format)
                ws.write(i, 15, goods['goods_no'], format)
                ws.write(i, 16, goods.get('provider_name', ''), format)
                ws.write(i, 17, goods['cat_id'], format)
                ws.write(i, 18, '|'.join(goods.get('cats', '')), format2)
                ws.write(i, 19, time.strftime("%Y-%m-%d %H:%M", time.localtime(row[14])), format2)
            # i += 1
            # ws.merge_range(i, 0, i, 9,'')
            print('成功处理分类 : %s' % (cat[1].encode('utf-8')))
        wb.close()
        print '成功导出Excel文件 : %s' % filename
        return filename

    def tohtml(self, element):
        if isinstance(element, list):
            return [self.tohtml(vo) for vo in element]
        return etree.tostring(element, method='html', encoding='unicode')

    def totext(self, element):
        if isinstance(element, list):
            return [self.totext(vo) for vo in element]
        return util.cleartext(etree.tostring(element, method='text', encoding='utf-8'))

