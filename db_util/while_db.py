# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

__doc__ = '''
导出芯城所有数据(代购, 合作商)
流程: 所有数据去重入mongodb, 然后从mongodb导出csv
'''

__author__ = 'billy'

import os
import sys
import csv
import time
import argparse
from threading import Thread
from multiprocessing import Process

reload(sys)
sys.setdefaultencoding('utf8')

try:
    import config
except ImportError:
    sys.path[0] = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
    import config
from packages import Util as util
from packages import hqchip


suppliers = 'chip1stop,mouser,supplier,arrow,verical,tme,digikey,element14,future,master,rs'

SavePath = os.path.join(config.APP_ROOT, 'database', 'all_hqchip_data.csv')

class Export_Hqchip(object):

    db_name = 'hqchip_alls'

    def _init_args(self, **kwargs):
        self._interval = kwargs.get('interval', 0.001)
        self.action = kwargs.get('action', 'import')
        self.max_threads = kwargs.get('threads', 3)
        self.max_process = kwargs.get('process', 3)
        self.month = kwargs.get('month', 6)
        self.start_time = int(time.time())
        self._brand_data = {}

    def __init__(self, **kwargs):
        self._init_args(**kwargs)
        if self.action == 'import':
            self.run()
            self.export_csv()
        elif self.action == 'export':
            self.export_csv()
        else:
            print '参数错误: action: {0}'.format(self.action)

    def run(self):
        dbs = suppliers.split(',')
        process_list = []
        for db_name in dbs:
            # 多进程获取不同db_data
            ptask = Process(target=self.get_db_data, args=(db_name,))
            ptask.start()
            process_list.append(ptask)
            if len(process_list) >= 1:
                for p in process_list:
                    p.join()
                process_list = []

    def get_db_data(self, db_name):
        _total_num = 0
        last_id = None
        condition = {'time': {'$gt': int(time.time() - 30*86400*self.month)}}
        self.mongo = hqchip.db.mongo[self.db_name]
        self.mongo.ensure_index('brand_name', unique=False)
        # 唯一标识
        self.mongo.ensure_index('goods_name', unique=True)
        self.mongo.ensure_index('goods_id', unique=True)
        collection = hqchip.db.mongo[db_name]
        task_list = []
        while 1:
            if last_id:
                condition['_id'] = {'$gt': last_id}
            dlist = collection.find(condition).sort([("_id", 1)]).limit(1000)
            n = 0
            for vo in dlist:
                n += 1
                if not vo['ModelName']:
                    continue
                # 不同代购数据入库 | 多线程导入db_data
                task = Thread(target=self.filter_db_data, args=(vo, db_name),)
                task.start()
                task_list.append(task)
                if len(task_list) > self.max_threads:
                    for t in task_list:
                        _total_num += 1
                        t.join()
                    task_list = []
                    print '记录当前db: {0} 的第 {1} 条数据'.format(db_name, _total_num)
                time.sleep(self._interval)
                print '------ time sleep {0} sec ------'.format(self._interval)
            if n <= 0:
                break
            last_id = vo['_id']
        return _total_num

    def filter_db_data(self, item, db_name):
        shop_price = item['Tiered'][-1][1]
        goods_number = item['Stock'][0]
        if db_name == 'supplier' and len(item['Tiered'][-1]) >= 3:
            shop_price = item['Tiered'][-1][2]
        increment = item['increment'] if item.get('increment', None) else 1
        db_data = {
            'goods_name': item['ModelName'],
            'brand_name': item['BrandName'],
            'package': increment,
            'desc': item['Desc'],
            'goods_number': goods_number,
            'shop_price': shop_price,
            'stock': item['Stock'],
            'tiered': item['Tiered'],
            'goods_id': item['GoodsId'],
        }
        info = self.mongo.find_one({
            'goods_name': db_data['goods_name']
        })
        if info:
            __id = info['_id']
            pre_stock = info['stock']
            pre_price = info['shop_price']
            update = False
            if pre_stock < db_data['stock']:
                update = True
            elif (db_data['shop_price'] != 0 and pre_price == 0) or db_data['shop_price'] < pre_price:
                update = True
            if update:
                self.mongo.update({'_id': __id}, {'$set': db_data})
                print 'db: {0} goods_name: {1} 更新数据成功'.format(db_name, db_data['goods_name'].encode('utf-8'))
            else:
                print 'db: {0} goods_name: {1} 跳过重复数据'.format(db_name, db_data['goods_name'].encode('utf-8'))
        else:
            try:
                self.mongo.insert(db_data)
                print 'db: {0} goods_name: {1} 保存数据成功'.format(db_name, db_data['goods_name'].encode('utf-8'))
            except Exception as e:
                print 'duplicate : {0} ******************'.format(e)

    def deal_data(self, data):
        csv_data = [data['goods_id'], data['goods_name'],data['brand_name'],data['package'],data['desc'],data['goods_number'],data['shop_price'],data['tiered']]
        self.writer.writerow(csv_data)
        print '型号: {0} 写入csv成功'.format(data['goods_name'])
        self._total_num += 1

    def export_csv(self):
        # 初始化参数
        self._total_num = 0
        last_id = None
        condition = {}
        task_list = []
        collection = hqchip.db.mongo[self.db_name]
        fp = open(SavePath, 'wb')
        self.writer = csv.writer(fp, dialect='excel')
        self.writer.writerow(['id', '型号', '品牌', '包装', '描述', '库存', '最低价', '完整价格'])
        while 1:
            if last_id:
                condition['_id'] = {'$gt': last_id}
            dlist = collection.find(condition).sort([("_id", 1)]).limit(1000)
            n = 0
            for vo in dlist:
                n += 1
                task = Thread(target=self.deal_data, args=(vo,))
                task.start()
                task_list.append(task)
                if len(task_list) > self.max_threads:
                    for t in task_list:
                        t.join()
                    task_list = []
                time.sleep(self._interval)
                print 'count_number: {0} ------ time sleep {1} sec ------'.format(self._total_num, self._interval)
            if n <= 0:
                break
            last_id = vo['_id']
        return self._total_num

def main():
    parser = argparse.ArgumentParser(description="华秋所有数据导出csv", add_help=False)

    parser.add_argument('-h', '--help', dest='help', help='获取帮助信息', action='store_true', default=False)
    parser.add_argument('-i', '--interval', dest='interval', help='每次抓取间隔时间，默认为0.01秒, 小于等于0时为不间隔',
                        default=0.01, type=int)
    # parser.add_argument('-p', '--process', dest='process', help='最大进程数,默认为3个', default=3, type=int)
    parser.add_argument('-t', '--threads', dest='threads', help='最大线程数,默认为4个', default=4, type=int)
    parser.add_argument('-m', '--month', dest='month', help='限制为最近几个月之内的数据, 默认为12个月', default=12, type=int)
    parser.add_argument('-r', '--import', dest='action', help='导入数据至缓存mongodb', action='store_const', const='import')
    parser.add_argument('-e', '--export', dest='action', help='从缓存mongodb中导出csv文件', action='store_const', const='export')
    args = parser.parse_args()
    if args.help:
        parser.print_help()
        print "\n帮助示例:"
        print "合并数据去重后导出csv               %s -r" % sys.argv[0]
        print "在已有的去重库中直接导出csv          %s -e" % sys.argv[0]
        print "指定最大线程数       %s -t 4" % sys.argv[0]
        print
        print '示例: python  -r -t 4 -m 12'
        print
    elif args.action:
        Export_Hqchip(**args.__dict__)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()