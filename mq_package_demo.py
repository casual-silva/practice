#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
from >> https://blog.csdn.net/wenhaodong58852219/article/details/84319566
'''

import pika
import hashlib
import json

def getMd5(input_str):
    """
    :param str input_str: Unicode-objects must be encoded before hashing
    :rtype: str
    """
    hash_obj = hashlib.md5(input_str.encode("utf-8"))
    return hash_obj.hexdigest()

class RabbitMQClient:
    """RabbitMQClient using pika library
    default: exchange type is 'topic', routing key is '#', dead letter exchange is 'DLX' and dead letter queue is 'DLQ'.
    """
    __default_exchange_type = "topic"
    # (hash) can substitute for zero or more words, * (star) can substitute for exactly one word.
    __default_routing_key = "#"
    __default_DeadLetterExchange = "DLX"
    __default_DeadLetterQueue = "DLQ"

    def __init__(self, username, password, host, port=5672):
        self.host = str(host)
        self.port = int(port)
        # set heartbeat=0, deactivate heartbeat default
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
			port=self.port, credentials=pika.PlainCredentials(username,password), heartbeat=0))  
        self.channel = self.connection.channel()

    #
    # basic operations
    #

    def close_connection(self):
        self.connection.close()

    def declare_exchange(self, exchange, exchange_type=__default_exchange_type):
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)

    def delete_exchange(self, exchange):
        self.channel.exchange_delete(exchange=exchange)

    def declare_queue(self, queue):
        self.channel.queue_declare(queue=queue, durable=True)

    def declare_queue_dlx(self, queue, dlx=__default_DeadLetterQueue):
        self.channel.queue_declare(queue=queue, durable=True, arguments={'x-dead-letter-exchange': dlx})

    def declare_queue_ttl(self, queue, ttl_seconds):
        self.channel.queue_declare(queue=queue, durable=True, arguments={'x-message-ttl': ttl_seconds})

    def delete_queue(self, queue):
        self.channel.queue_delete(queue=queue)

    def bind_exchange_queue(self, queue, exchange, binding_key=__default_routing_key):
        self.channel.queue_bind(queue=queue, exchange=exchange, routing_key=binding_key)

    #
    # combined operations
    #

    def declare_dlx_dlq(self, dlx=__default_DeadLetterExchange, dlq=__default_DeadLetterQueue):
        """
        :param str dlx: dead letter exchange
        :param str dlq: dead letter queue
        """

        self.declare_exchange(exchange=dlx, exchange_type='fanout')
        self.declare_queue(queue=dlq)
        self.bind_exchange_queue(exchange=dlx, queue=dlq)

    def publish(self, message, exchange, queue, routing_key, message_id=None,         
        close_connection=True):
        """
        publish messages with message_id, disk persistency property
        """

        if message_id is None:
            message_id = getMd5(input_str=message)
        self.declare_queue(queue=queue)
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message,
            properties=pika.BasicProperties(delivery_mode=2,message_id=message_id,content_type="application/json"))
        if close_connection:
            self.close_connection()

    def consume(self, callback, queue, dlx=__default_DeadLetterExchange, dlq=__default_DeadLetterQueue, 
        exclusive=False, consumer_tag=None,**kwargs):
        self.declare_dlx_dlq(dlx=dlx, dlq=dlq)
        self.channel.basic_consume(queue=queue, on_message_callback=callback, exclusive=exclusive,
            consumer_tag=consumer_tag,**kwargs)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.close_connection()

        
    @staticmethod
    def ack_message(channel, method):
        channel.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    def reject_to_dlx(channel, method):
        """
        need the queue from which message is consuming has dead letter exchage property
        """
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def transmit(channel, method, properties, message, exchange=__default_DeadLetterExchange, 
        routing_key=__default_routing_key, queue=__default_DeadLetterQueue,handler=None):
        if handler is not None:
            message = handler(message)
        message_id = properties.message_id
        if message_id is None:
            message_id = getMd5(input_str=message)
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message,
            properties=pika.BasicProperties(delivery_mode=2,message_id=message_id,content_type="application/json"))
        channel.basic_ack(delivery_tag=method.delivery_tag)

def callback(ch, method, properties, body):
    print("consumer_tag %r, consume_func %r, %r" % (method.consumer_tag, method.routing_key, properties.message_id))
    # RabbitMQClient.transmit(channel=ch, method=method, properties=properties, message=str(body, 'utf-8'), handler=handler)
    RabbitMQClient.ack_message(channel=ch, method=method)

def handler(input_str):
    return "hadled"+input_str

if __name__ == "__main__":
    mqc = RabbitMQClient(username='xxx',password='xxx',host='xxx',port=5672)
    msg = json.dumps({'a':'aaa'})
    queue = "DLQ"
    # mqc.publish(message=msg, exchange='', routing_key=queue, queue=queue)
    # mqc.consume(callback=callback, queue=queue, consumer_tag='consumer-1')    
    print("==done==")