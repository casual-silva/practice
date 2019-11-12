    def check_goods(self):
        """检测数据有效性"""
        last_id = 0
        _total_num = 0
        collect = getattr(self.mongo, 'supplier')
        _unix_time = int(time.time()) - 8 * 3600
        while 1:
            condition = {
                'goods_id': ('>', last_id),
                'PN2': PN2
            }
            goods_list = self.supplier.select('goods', condition=condition,
                                              fields=('goods_id', 'last_update'),
                                              order='goods_id ASC',
                                              limit=1000)
            if not goods_list:
                break
            goods_id = 0
            for row in goods_list:
                goods_id = row['goods_id']
                if (row['last_update'] + 8 * 3600) >= self._start_time:
                    print('产品 %s 有效' % (goods_id,))
                else:
                    mongo_data = {
                        'error': 404,
                        'time': int(time.time()),
                    }
                    info = collect.find_one({'GoodsId': goods_id})
                    if info:
                        collect.update_one({'GoodsId': goods_id}, {"$set": mongo_data})
                        print('无效产品：%s, 更新mongodb成功' % (goods_id,))
                _total_num += 1
            last_id = goods_id
        # 更新供应商最后更新时间
        self.hqchip.update('suppliers', condition={'supplier_sn': PN2}, data={
            'last_update': _unix_time
        })
        return _total_num