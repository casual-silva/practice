# -*- encoding: utf-8 -*-

__author__ = 'qaulau'

import time
import Util as util


#比较式
_comparison = {'eq':'=','neq':'<>','gt':'>','egt':'>=','lt':'<','elt':'<=','notlike':'NOT LIKE','notin':'NOT IN','!like':'NOT LIKE'}


def implode_field_value(array, glue=',', fields=None, encape='`'):
    '''
    连接数组中的字段及值转为字符串

    @param dict or list     array ：需要转换的数据
    @param string           glue  : 连接字符

    @return 处理后的sql字符串语句

    2014/09/12 添加exp，可用于直接执行SQL函数和语句如字段递增等; example: insert('order',data = {'num':('exp','num + 1')})
    '''
    args = []
    if isinstance(array, list):
        array = dict(array)
    sql = comma = ''
    for k in array:
        if isinstance(array[k], (list, tuple)):
            if fields and k not in fields:
                continue
            opt = str(array[k][0]).strip().lower()
            # Fix: {'goods_id': (1,)}
            if len(array[k]) == 1:
                sql += "%s%s%s%s = %%s" % (comma, encape, k, encape)
                args.append(array[k][0])
            elif opt == 'exp':
                if glue == ',':
                    sql += "%s%s%s%s = %s" % (comma, encape, k, encape, array[k][1])
                else:
                    sql += "%s(%s%s%s %s)" % (comma, encape, k, encape, array[k][1])
            else:
                if opt in _comparison:
                    opt = _comparison[opt]
                opt = opt.upper()
                if opt in ('NOT IN', 'IN'):
                    _in_sql = '(' + ', '.join(['%s'] * len(array[k][1])) + ')'
                    sql += '%s%s%s%s %s %s' % (comma, encape, k, encape, opt, _in_sql)
                    args.extend(array[k][1])
                else:
                    sql += "%s%s%s%s %s %%s" % (comma, encape, k, encape, opt)
                    args.append(array[k][1])
        else:
            if fields and k not in fields:
                continue
            sql += "%s%s%s%s = %%s" % (comma, encape, k, encape)
            args.append(array[k])
        comma = glue
    return sql, args


def implode_condition(args, encape='`'):
    '''
    连接条件语句

    args : 条件语句
    示例        [('id',1),'|',('status','<',1)] 其等价于 id = 1 or status < 1
                [('id',1),'|',[('status','<',1),('name','like','qaulau')]] 其等价于 id = '1' or (status < '1' AND name like '%qaulau%')
                [('id',1),'|',[('status','<',1),('name','like','qaulau'),[('like','like','computer'),'|',('age','>',18)]]]
                其等价于 id = '1' or (status < '1' AND name like '%qaulau%' AND (`like` like '%computer%' or `age` > 18))
                [('id',1),('status','<',1)] 其等价于 id = 1 and status < 1
                {'id':1,'status':('<',1)}  其等价于 id = 1 and status < 1
    '''
    global _comparison
    def _get_expression(args, params=None, encape='`'):
        comma = query = ''
        for arg in args:
            if isinstance(arg, list):
                query += "%s (%s)" % (comma, _get_expression(arg, params=params, encape=encape))
                comma = ' AND'
            elif isinstance(arg, tuple):
                if len(arg) == 2:
                    query += "%s %s%s%s = %%s" % (comma, encape, arg[0], encape)
                    params.append(arg[1])
                else:
                    opt = str(arg[1]).strip().lower()
                    if opt in _comparison:
                        opt = _comparison[opt]
                    opt = opt.upper()
                    _append_args = 1
                    if 'LIKE' in opt:
                        if '%' not in arg[2]:
                            query += "%s %s%s%s %s '%%%%%s%%%%'" % (comma, encape, arg[0], encape, opt, arg[2])
                            _append_args = 0
                        else:
                            query += "%s %s%s%s %s %%s" % (comma, encape, arg[0], encape, opt)
                    else:
                        query += "%s %s%s%s %s %%s" % (comma, encape, arg[0], encape, opt)
                    if _append_args:
                        if isinstance(arg[2], list):
                            arg[2] = tuple(arg[2])
                        params.append(arg[2])
                comma = ' AND'
            elif arg in ['|', 'or', '!', '', 'OR']:
                comma = ' OR'
        return query

    if isinstance(args, dict):
        return implode_field_value(args, ' AND ', encape=encape)
    elif isinstance(args, list):
        params = []
        query = _get_expression(args, params=params, encape=encape)
        return query, params

class DBException(Exception):
    pass


class DBTableNotExists(DBException):
    pass


class db_mysql(object):
    '''
    基于MySQLdb库封装mysql常用操作，避免繁琐的字符串拼接操作，同时方便处理特殊字符，无需手动转义字符串
    2014/07/31



    以下方法中codition为限制条件，可以为字典和列表
              example ： {'name':'qaulau'}


              data 为更新或添加的数据，可以为字典或者列表（列表必须为列表或元祖对，即[(key,val),...]）
                   键值对应为字段名
              example : insert('order',data = {'name':'qaulau','create_time':121545015})

    2014-8-27 添加字段自动匹配，对于数据表中不存在的字段会自动过滤（仅针对更新和插入的数据集，限制条件不在此列）

    '''
    driver = 'MySQLdb'
    rety_count = 3    # 最大重试次数
    tablepre = ''
    data_type = None
    interval = 5      # 重连间隔时间

    def __init__(self, *args, **kwargs):
        '''
        db_fields_cache 为是否缓存数据字段，默认为不缓存，在一次连接中会查询一次字段值，如果选择True如果更新了字段请手动删除缓存字段

        '''
        if args and isinstance(args[0], dict):
            kwargs.update(args[0])
        if 'charset' not in kwargs:
            kwargs['charset'] = 'utf8'
        self._trans_times = 0
        self.db_fields_cache = kwargs.get('db_fields_cache', False)
        self.tablepre = kwargs.get('tablepre', '')
        self.dbname = kwargs.get('db', None)
        self.host = kwargs.get('host', None)
        self.fields = {}
        self.__pks = {}
        args = kwargs.copy()
        if 'db_fields_cache' in args:
            del args['db_fields_cache']
        if 'tablepre' in args:
            del args['tablepre']
        if 'data_type' in args:
            del args['data_type']
        self.args = args
        if kwargs.get('data_type', '') == 'dict':
            self.data_type = 'dict'
        self._connect()

    @property
    def dbapi(self):
        return __import__(self.driver)

    def _connect(self):
        '''
        连接数据库
        :return:
        '''
        self.conn = self.dbapi.connect(**self.args)
        if self.data_type == 'dict':
            self.cur = self.conn.cursor(cursorclass=self.dbapi.cursors.DictCursor)
        else:
            self.cur = self.conn.cursor()

    def select_db(self, db):
        '''
        选择数据库
        '''
        self.dbname = db
        self.args['db'] = db
        self.conn.select_db(db)

    def table(self, table_name):
        '''
        获取带前缀的表名
        '''
        return '%s%s' % (self.tablepre, table_name)

    def _check_table_info(self, table_name):
        #只在第一次执行记录
        if table_name not in self.fields:
            #如果数据表字段没有定义则自动获取
            if self.db_fields_cache:
                self.fields[table_name] = util.file('.fields/%s/%s_%s_%s' % (self.host, self.__class__.__name__, self.dbname, table_name))
                if not self.fields[table_name]:
                    self.flush(table_name)
            else:
                #每次都会读取数据表信息
                self.flush(table_name)

    def flush(self, table_name):
        '''
        刷新字段数据
        '''
        fields = self.get_fields(table_name)
        if not fields:
            return False
        self.fields[table_name] = fields
        if self.db_fields_cache:
            util.file('.fields/%s/%s_%s_%s' % (self.host, self.__class__.__name__, self.dbname, table_name), fields)


    def get_fields(self, table_name):
        '''
        获取字段列表
        '''
        result = self.query('SHOW COLUMNS FROM %s;' % table_name)
        info = []
        if result:
            for val in result:
                if isinstance(val, dict):
                    f = val['Field']
                else:
                    f = val[0]
                if isinstance(f, unicode):
                    f = f.encode('utf-8')
                info.append(f)
        return info

    def get_pk(self, table):
        '''
        获取表table的主键
        :return:
        '''
        table_name = self.table(table)
        if table_name in self.__pks:
            return self.__pks[table_name]
        result = self.query("SHOW COLUMNS FROM %s WHERE `key` = 'PRI';" % table_name)
        pk = ''
        if result:
            for val in result:
                if isinstance(val, dict):
                    pk = val['Field']
                else:
                    pk = val[0]
                break
        self.__pks[table_name] = pk
        return pk

    def query(self, query, args=None):
        '''
        执行sql语句
        '''
        self.execute(query, args=args)
        return self.fetchall()

    def execute(self, query, args=None , _num=0):
        '''
        执行sql语句
        '''
        try:
            return self.cur.execute(query, args=args)
        except self.dbapi.OperationalError as e:
            if _num == self.rety_count:
                raise self.dbapi.OperationalError(e)
            else:
                # 延时重连
                if self.interval:
                    print('------ sleep %s sec rety connect ------' % (self.interval,))
                    time.sleep(self.interval)
                self._connect()
                self.execute(query, args=args, _num=_num + 1)

    def insert(self, table, data={}, return_insert_id=False, replace=False, **kwargs):
        '''
        插入数据

        @param string  table：不带前缀的表名
        @param dict    data : 插入数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 插入数据库的数据，字段名：数值
        @param boolean return_insert_id：是否返回插入数据的ID
        @param boolean replace：是否替换

        @return 如果return_insert_id为真则会返回插入数据ID；否则返回真或假
        '''
        data.update(kwargs)
        table = self.table(table)
        self._check_table_info(table)
        if isinstance(data, (dict, list)):
            try:
                query, args = implode_field_value(data, fields=self.fields[table])
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        else:
            query = data
            args = None
        cmd = 'REPLACE INTO' if replace else 'INSERT INTO'
        self.execute("%s `%s` SET %s;" % (cmd, table, query), args)
        rs = self.insert_id() if return_insert_id else self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs

    def update(self, table, data={}, condition=None, low_priority=False, **kwargs):
        '''
        更新数据

        @param string   table : 数据库名称
        @param dict   data : 更新数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 更新数据库的数据，字段名：数值
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param tuple   args : 可以是直接字典数据
        @param dict    kwargs ： 字段名：数值

        @return 返回None
        '''
        data.update(kwargs)
        if not data:
            raise DBException("update data doesn't exist empty!")
        table = self.table(table)
        self._check_table_info(table)
        try:
            sql, args1 = implode_field_value(data, fields=self.fields[table])
        except KeyError:
            raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        cmd = "UPDATE " + ('LOW_PRIORITY' if low_priority else '')
        where = ''
        args2 = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args2 = implode_condition(condition)
        else:
            where = condition
        args = None
        if args1 is not None:
            args = args1
            if args2 is not None:
                args.extend(args2)
        self.execute("%s `%s` SET %s WHERE %s;" % (cmd, table, sql, where), args)
        if self._trans_times == 0:
            self.conn.commit()
        return self.affected_rows()

    def select(self, table, fields=None, condition=None, order=None, limit=0):
        '''
        查询数据

        @param string   table : 数据库名称
        @param list or tuple fields : 查询字段名
        @param dict     condition : 限制条件， [('id','>','10'),|,('status',1)]
        @param string   limit : 限制性条件（默认为0)

        @return 如果limit为1则返回一个结果字典否则返回列表
        '''
        table = self.table(table)
        if fields is None:
            self._check_table_info(table)
            try:
                fields = self.fields[table]
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        if isinstance(fields, (list, tuple)):
            _fields = ''
            for field in fields:
                _fields += ',`%s`' % field
            fields = _fields[1:]
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition)
        else:
            where = condition
        order = '' if order is None else 'ORDER BY %s' % order
        sql = "SELECT %s FROM `%s` WHERE %s %s %s;" % (fields, table, where, order, 'LIMIT %s' % limit if limit else '')
        self.execute(sql, args)
        if self._trans_times == 0:
            self.conn.commit()
        return self.cur.fetchone() if limit == 1 else self.cur.fetchall()

    def delete(self, table, condition=None, limit=0):
        '''
        删除数据

        @param string   table : 数据库名称
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param string   limit : 限制性条件（默认为0)

        @return 返回影响的条数
        '''
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition)
        else:
            where = condition
        sql = "DELETE FROM `%s` WHERE %s %s;" % (self.table(table), where, 'LIMIT %s' % limit if limit else '')
        self.execute(sql, args)
        rs = self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs

    def count(self, table, condition=None, pk=None):
        '''
        获取表中数据

        :param table:
        :param condition:
        :param pk:
        :return:
        '''
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition)
        else:
            where = condition
        if not pk:
            pk = self.get_pk(table)
        if not pk:
            pk = 'id'
        sql = "SELECT COUNT(%s) AS c FROM %s WHERE %s LIMIT 1;" % (pk, self.table(table), where)
        self.execute(sql, args)
        ret = self.fetchone()
        if hasattr(ret, 'get'):
            return ret['c']
        return ret[0]

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def fecthmany(self, size=None):
        return self.cur.fetchmany(size=size)

    def result_first(self, sql):
        self.query(sql)
        return self.fetchone()

    def result_all(self, sql):
        self.query(sql)
        return self.fetchall()

    def insert_id(self):
        '''
        获取最后一次插入数据的主键ID
        '''
        return self.conn.insert_id()

    def num_rows(self):
        '''
        取得结果集中行的数目
        '''
        return self.cur.rownumber

    def affected_rows(self):
        '''
        返回上一步SQL操作受影响的行数
        '''
        return self.cur.rowcount

    def start_trans(self):
        '''
        启动事物
        :return:
        '''
        self.conn.commit()
        if self._trans_times == 0:
            self.execute('START TRANSACTION;')
            self._trans_times += 1
        return True

    def commit(self):
        '''
        提交事物
        :return:
        '''
        if self._trans_times > 0:
            self._trans_times = 0
        return self.conn.commit()

    def rollback(self):
        '''
        回滚事物
        :return:
        '''
        if self._trans_times > 0:
            self.conn.rollback()
            self._trans_times = 0
        return True

    def version(self):
        '''
        返回mysql版本
        '''
        res = self.query('SELECT VERSION() AS ver')
        if isinstance(res[0],dict):
            return res[0]['ver']
        return res[0][0]

    def get_lastsql(self):
        '''
        返回上一步操作sql语句
        '''
        return self.cur._last_executed

    def close(self):
        '''
        关闭mysql
        '''
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def __del__(self):
        self.close()


class db_sqlite:
    pass

class db_mongo:
    pass

class db_postgre(db_mysql):

    driver = 'psycopg2'

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            kwargs.update(args[0])
        self._trans_times = 0
        self.db_fields_cache = kwargs.get('db_fields_cache', False)
        self.tablepre = kwargs.get('tablepre', '')
        self.dbname = kwargs.get('dbname', None)
        self.host = kwargs.get('host', None)
        self.fields = {}
        _dsn = ''
        for p in ('host', 'port', 'user', 'password','dbname'):
            _dsn += '%s=%s ' % (p, kwargs.get(p, None))
        self.dsn = _dsn
        self.conn = None
        if kwargs.get('data_type', '') == 'dict':
            self.data_type = 'dict'
        self._connect()

    def _connect(self):
        '''
        连接数据库
        :return:
        '''
        self.conn = self.dbapi.connect(self.dsn)
        if self.data_type == 'dict':
            __import__(self.dbapi.__name__ + '.extras')
            self.cur = self.conn.cursor(cursor_factory=self.dbapi.extras.DictCursor)
        else:
            self.cur = self.conn.cursor()

    def get_fields(self, table_name):
        '''
        获取字段列表
        :param table_name:
        :return:
        '''
        result = self.query('SELECT column_name FROM information_schema.columns WHERE table_name = %s;', (table_name,))
        info = []
        if result:
            for val in result:
                if isinstance(val, dict):
                    info.append(val['Field'])
                else:
                    info.append(val[0])
        return info

    def query(self, query, args=None):
        '''
        执行sql语句
        '''
        self.execute(query, args)
        return self.fetchall()

    def execute(self, query, args=None , _num = 0):
        '''
        执行sql语句
        '''
        try:
            return self.cur.execute(query, args)
        except self.dbapi.OperationalError as e:
            if _num == self.rety_count:
                raise self.dbapi.OperationalError(e)
            else:
                self._connect()
                self.execute(query, args=args,_num = _num + 1)

    def insert(self, table, data={}, return_insert_id=False, replace=False, **kwargs):
        '''
        插入数据

        @param string  table：不带前缀的表名
        @param dict    data : 插入数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 插入数据库的数据，字段名：数值
        @param boolean return_insert_id：是否返回插入数据的ID
        @param boolean replace：是否替换

        @return 如果return_insert_id为真则会返回插入数据ID；否则返回真或假
        '''
        data.update(kwargs)
        table = self.table(table)
        self._check_table_info(table)
        if isinstance(data, (dict, list)):
            try:
                query, args = implode_field_value(data, fields=self.fields[table], encape='')
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        else:
            query = data
            args = None
        cmd = 'REPLACE INTO' if replace else 'INSERT INTO'
        self.execute("%s %s SET %s" % (cmd, table, query), args)
        rs = self.insert_id() if return_insert_id else self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs

    def update(self, table, data={}, condition=None, **kwargs):
        '''
        更新数据

        @param string   table : 数据库名称
        @param dict   data : 更新数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 更新数据库的数据，字段名：数值
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param tuple   args : 可以是直接字典数据
        @param dict    kwargs ： 字段名：数值

        @return 返回None
        '''
        data.update(kwargs)
        if not data:
            raise DBException("update data doesn't exist empty!")
        table = self.table(table)
        self._check_table_info(table)
        try:
            sql, args1 = implode_field_value(data, fields=self.fields[table], encape='')
        except KeyError:
            raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        cmd = "UPDATE "
        where = ''
        args2 = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args2 = implode_condition(condition, encape='')
        else:
            where = condition
        args = None
        if args1 is not None:
            args = args1
            if args2 is not None:
                args.extend(args2)
        self.execute("%s %s SET %s WHERE %s" % (cmd, table, sql, where), args)
        if self._trans_times == 0:
            self.conn.commit()
        return self.affected_rows()

    def select(self, table, fields=None, condition=None, order=None, limit=0):
        '''
        查询数据

        @param string   table : 数据库名称
        @param list or tuple fields : 查询字段名
        @param dict     condition : 限制条件， [('id','>','10'),|,('status',1)]
        @param string   limit : 限制性条件（默认为0)

        @return 如果limit为1则返回一个结果字典否则返回列表
        '''
        table = self.table(table)
        if fields is None:
            self._check_table_info(table)
            try:
                fields = self.fields[table]
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        if isinstance(fields, (list, tuple)):
            _fields = ''
            for field in fields:
                _fields += ',%s' % field
            fields = _fields[1:]
        args = None
        if not condition:
            where = '1 = 1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition, encape='')
        else:
            where = condition
        order = '' if order is None else 'ORDER BY %s' % order
        sql = "SELECT %s FROM %s WHERE %s %s %s" % (fields, table, where, order, 'LIMIT %s' % limit if limit else '')
        self.execute(sql, args)
        if self._trans_times == 0:
            self.conn.commit()
        return self.cur.fetchone() if limit == 1 else self.cur.fetchall()

    def delete(self, table, condition=None, limit=0):
        '''
        删除数据

        @param string   table : 数据库名称
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param string   limit : 限制性条件（默认为0)

        @return 返回影响的条数
        '''
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition, encape='')
        else:
            where = condition
        sql = "DELETE FROM %s WHERE %s %s" % (self.table(table), where, 'LIMIT %s' % limit if limit else '')
        self.execute(sql, args)
        rs = self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs

    def get_lastsql(self):
        return self.cur.query

    def insert_id(self):
        return self.query('SELECT LASTVAL();')[0][0]


class db_mssql(db_mysql):
    """SQL Server"""

    driver = 'pymssql'

    def __init__(self, *args, **kwargs):
        super(db_mssql, self).__init__(*args, **kwargs)
        self._last_executed = None

    def _connect(self):
        '''
        连接数据库
        :return:
        '''
        self.conn = self.dbapi.connect(**self.args)
        if self.data_type == 'dict':
            self.cur = self.conn.cursor(as_dict=True)
        else:
            self.cur = self.conn.cursor()

    def get_fields(self, table_name):
        '''
        获取字段列表
        :param table_name:
        :return:
        '''
        result = self.query("SELECT COLUMN_NAME AS Field,DATA_TYPE FROM INFORMATION_SCHEMA.columns \
            WHERE TABLE_NAME= '%s';" % (table_name,))
        info = []
        if result:
            for val in result:
                if isinstance(val, dict):
                    info.append(val['Field'].lower())
                else:
                    info.append(val[0].lower())
        return info

    def execute(self, query, args=None , _num = 0):
        '''
        执行sql语句
        '''
        try:
            self._last_executed = (query, args)
            if isinstance(args, list):
                args = tuple(args)
            return self.cur.execute(query, args)
        except self.dbapi.OperationalError as e:
            if _num == self.rety_count:
                raise self.dbapi.OperationalError(e)
            else:
                self._connect()
                self.execute(query, args=args, _num =_num +1)
                
    def insert(self, table, data={}, return_insert_id=False, replace=False, **kwargs):
        '''
        插入数据

        @param string  table：不带前缀的表名
        @param dict    data : 插入数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 插入数据库的数据，字段名：数值
        @param boolean return_insert_id：是否返回插入数据的ID
        @param boolean replace：是否替换

        @return 如果return_insert_id为真则会返回插入数据ID；否则返回真或假
        '''
        data.update(kwargs)
        table = self.table(table)
        self._check_table_info(table)
        if isinstance(data, (dict, list)):
            try:
                query, args = implode_field_value(data, fields=self.fields[table], encape='')
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        else:
            query = data
            args = None
        cmd = 'REPLACE INTO' if replace else 'INSERT INTO'
        self.execute("%s %s SET %s" % (cmd, table, query), args)
        rs = self.insert_id() if return_insert_id else self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs

    def update(self, table, data={}, condition=None, **kwargs):
        '''
        更新数据

        @param string   table : 数据库名称
        @param dict   data : 更新数据库的数据，可以是直接字典数据
        @param dict    kwargs ： 更新数据库的数据，字段名：数值
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param tuple   args : 可以是直接字典数据
        @param dict    kwargs ： 字段名：数值

        @return 返回None
        '''
        data.update(kwargs)
        if not data:
            raise DBException("update data doesn't exist empty!")
        table = self.table(table)
        self._check_table_info(table)
        try:
            sql, args1 = implode_field_value(data, fields=self.fields[table], encape='')
        except KeyError:
            raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        cmd = "UPDATE "
        where = ''
        args2 = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args2 = implode_condition(condition, encape='')
        else:
            where = condition
        args = None
        if args1 is not None:
            args = args1
            if args2 is not None:
                args.extend(args2)
        self.execute("%s %s SET %s WHERE %s" % (cmd, table, sql, where), args)
        if self._trans_times == 0:
            self.conn.commit()
        return self.affected_rows()

    def select(self, table, fields=None, condition=None, order=None, limit=0):
        '''
        查询数据

        @param string   table : 数据库名称
        @param list or tuple fields : 查询字段名
        @param dict     condition : 限制条件， [('id','>','10'),|,('status',1)]
        @param string   limit : 限制性条件（默认为0)

        @return 如果limit为1则返回一个结果字典否则返回列表
        '''
        table = self.table(table)
        if fields is None:
            self._check_table_info(table)
            try:
                fields = self.fields[table]
            except KeyError:
                raise DBTableNotExists("Table %s doesn't exist!" % (table,))
        if isinstance(fields, (list, tuple)):
            _fields = ''
            for field in fields:
                _fields += ',%s' % field
            fields = _fields[1:]
        args = None
        if not condition:
            where = '1 = 1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition, encape='')
        else:
            where = condition
        order = '' if order is None else 'ORDER BY %s' % order
        sql = "SELECT %s %s FROM %s WHERE %s %s" % ('TOP %s' % limit if limit else '', fields, table, where, order)
        self.execute(sql, args)
        return self.cur.fetchone() if limit == 1 else self.cur.fetchall()

    def delete(self, table, condition=None, limit=0):
        '''
        删除数据

        @param string   table : 数据库名称
        @param dict     condition : 限制条件， {'id' : '> 10','status':1}
        @param string   limit : 限制性条件（默认为0)

        @return 返回影响的条数
        '''
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition, encape='')
        else:
            where = condition
        sql = "DELETE FROM %s WHERE %s %s" % (self.table(table), where, 'LIMIT %s' % limit if limit else '')
        self.execute(sql, args)
        rs = self.affected_rows()
        if self._trans_times == 0:
            self.conn.commit()
        return rs                

    def get_lastsql(self):
        '''
        返回上一步操作sql语句
        '''
        return self._last_executed

    def count(self, table, condition=None, pk=None):
        '''
        获取表中数据

        :param table:
        :param condition:
        :param pk:
        :return:
        '''
        args = None
        if not condition:
            where = '1'
        elif isinstance(condition, (dict, list)):
            where, args = implode_condition(condition, '')
        else:
            where = condition
        if not pk:
            pk = self.get_pk(table)
        if not pk:
            pk = 'id'
        sql = "SELECT COUNT(%s) AS c FROM %s WHERE %s;" % (pk, self.table(table), where)
        self.execute(sql, args)
        ret = self.fetchone()
        if hasattr(ret, 'get'):
            return ret['c']
        return ret[0]