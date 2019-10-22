# -*- encoding: utf-8 -*-

__author__ = "qaulau"


import time
try:
    from Queue import Empty
except:
    from queue import Empty
import threading
import socket
import select
try:
    import json
except ImportError:
    import simplejson as json
import pika
import config
import Util as util


def catch_except(fn):
    def wrap(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except (select.error, socket.error, pika.exceptions.ConnectionClosed, 
                pika.exceptions.AMQPConnectionError, AttributeError) as e:
            #print(e)
            self.connect()
            return fn(self, *args, **kwargs)
    return wrap


class RabbitMQ(object):

    connection = None
    channel = None
    delay = 0.01
    lastname = None

    def __init__(self, dsn=None):
        self.lock = threading.Lock()
        self._last_ack = None
        self.dsn = config.AMQP_URL if not dsn else dsn

    def connect(self):
        """连接队列"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.dsn))
            channel = connection.channel()
            self.connection = connection
            self.channel = channel
        except pika.exceptions.AMQPConnectionError:
            print('------------ sleep 5 sec ---------------')
            time.sleep(5)
            self.connect()

    def __check_connect(self):
        """检测连接"""
        if self.connection is None or self.connection.is_closed:
            self.connect()
        if self.channel is None or self.channel.is_closed:
            self.connect()

    def get_queue_list(self, queue_name=None, limit=30, exchange=None):
        '''
        获取队列列表
        '''
        if not queue_name:
            return None
        queue_list = []
        try:
            self.declare(queue_name, exchange=exchange)
            def callback(ch, method, properties, body):
                queue_list.append(json.loads(body))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            self.channel.basic_qos(prefetch_count=limit) #单次拿去数量
            self.channel.basic_consume(callback, queue=queue_name)
            self.close()
            return queue_list
        except Exception as e:
            print e
            return None

    def put_queue_list(self, queue_name=None, message_list=None, print_info=True, exchange=''):
        '''提交异常至队列列表'''
        if not queue_name and not exchange:
            return None
        try:
            if not message_list:
                return None
            if isinstance(message_list, dict):
                message_list = [message_list]
            self.declare(queue_name, exchange=exchange)
            for message in message_list:
                if print_info:
                    if 'goods_sn' in message:
                        print('GoodsSn : %s 数据已提交至队列 %s' % 
                              (util.binary_type(message['goods_sn']), queue_name))
                    elif 'product_id' in message:
                        print('ProductID : %s 数据已提交至队列 %s' % 
                              (util.binary_type(message['product_id']), queue_name))
                    elif 'kw' in message:
                        print('KeyWord : %s 数据已提交至队列 %s' %
                              (util.binary_type(message['kw']), queue_name))
                    elif 'goods_name' in message:
                        print('GoodsName : %s 数据已提交至队列 %s' % 
                              (util.binary_type(message['goods_name']), queue_name))
                    elif 'goods_id' in message:
                        print('GoodsID : %s 数据已提交至队列 %s' % 
                              (util.binary_type(message['goods_id']), queue_name))
                    elif 'id' in message:
                        print('ID : %s 数据已提交至队列 %s' % 
                              (util.binary_type(message['id']), queue_name))
                    elif 'keyword' in message:
                        print 'KeyWord : {0} 数据已提交至队列 {1}'.format(util.binary_type(message['keyword']), queue_name)
                message=json.dumps(message)
                self.channel.basic_publish(exchange=exchange,
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode = 2, #持久化
                    )
                )
            self.close()
        except Exception as e:
            print util.traceback_info(e)
            return None

    def qsize(self, queue_name=None):
        '''获取队列数据数目大小'''
        if not queue_name:
            return 0
        try:
            self.__check_connect()
            ret = self.channel.queue_declare(queue_name, passive=True)
            qsize = ret.method.message_count
            self.close()
            return qsize
        except Exception as e:
            print e
            return 0

    def purge(self, queue_name=None, exchange=None):
        '''清空队列数据'''
        if not queue_name:
            return None
        try:
            self.declare(queue_name, exchange=exchange)
            return self.channel.queue_purge(queue_name)
        except Exception as e:
            print e
            return None
        finally:
            self.close()

    @catch_except
    def put(self, queue_name, item, callback=json.dumps, exchange='', declare=True, routing_key=None):
        """提交数据"""
        with self.lock:
            if declare:
                self.declare(queue_name, exchange=exchange)
            if queue_name is None:
                queue_name = self.lastname
            if callback and callable(callback):
                item = callback(item)
            if item is None:
                return None
            if routing_key is None:
                routing_key = queue_name
            return self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key, 
                body=item,
                properties=pika.BasicProperties(
                    delivery_mode = 2,
                )
            )
        return True

    @catch_except
    def get(self, queue_name, ack=True, callback=json.loads, exchange=None, declare=True):
        """获取数据"""
        with self.lock:
            if declare:
                self.declare(queue_name, exchange=exchange)
            method_frame, header_frame, body = self.channel.basic_get(queue_name)
            if method_frame is None:
                return None
                raise Empty
            if ack:
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                self._last_ack = method_frame.delivery_tag
        if callback and callable(callback):
            return callback(body)
        return body


    def existed(self, queue_name=None):
        """检测队列是否存在"""
        if not queue_name:
            return None
        try:
            self.__check_connect()
            self.channel.queue_declare(queue=queue_name, passive=True, durable=False)
            return True
        except pika.exceptions.ChannelClosed as e:
            if e.args and e.args[0] == 404:
                return False
            return None

    @catch_except
    def declare(self, queue_name=None, exchange=None):
        """检测创建指定队列"""
        if not queue_name and not exchange:
            return None
        self.__check_connect()
        if self.channel.is_closed:
            self.channel = self.connection.channel()
        if queue_name:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.lastname = queue_name
        if exchange:
            self.channel.exchange_declare(exchange=exchange, exchange_type='fanout')
            if queue_name:
                self.channel.queue_bind(exchange=exchange, queue=queue_name)
        return True

    @catch_except   
    def consuming(self, queue_name, callback, exchange=None, declare=True, no_ack=True):
        """消费运行模式持续监听，处理队列数据"""
        if declare:
            self.declare(queue_name, exchange=exchange)
        if queue_name is None:
            queue_name = self.lastname
        self.channel.basic_consume(callback, queue=queue_name, no_ack=no_ack)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def close(self):
        try:
            self.channel.close()
            self.channel = None
        except:
            pass
        try:
            self.connection.close()
            self.connection = None
        except:
            pass

    def __delete__(self):
        self.close()