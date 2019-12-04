def run(self):
    _total_num = 0
    last_id = None
    condition = {}
    qname = 'qname'
    collect = self.mongo[qname]
    while 1:
        if last_id:
            condition['_id'] = {'$gt': last_id}
        dlist = collect.find(condition).sort([("_id", 1)]).limit(1000)
        n = 0
        for vo in dlist:
            n += 1
            if self.save_data(vo):
                _total_num += 1
        if n <= 0:
            break
        last_id = vo['_id']
    return _total_num