# -*- encoding: utf-8 -*-

__author__ = "qaulau"


import sys
import os
import logging
from functools import wraps
try:
    import json
except ImportError:
    import simplejson as json

from gevent.pywsgi import WSGIServer
import geventwebsocket
from geventwebsocket.handler import WebSocketHandler


_logger = None
MAX_THREAD = 5


class WebSocketsLogHandler(logging.Handler):

    def __init__(self, socket=None):
        logging.Handler.__init__(self)
        self.ws = socket

    def update_ws(self, socket=None):
        self.ws = socket

    def flush(self):
        pass

    def emit(self, record):
        try:
            if self.ws is None or self.ws.closed:
                return
            msg = self.format(record)
            data = {
                'type': 'output' if record.levelname != 'ERROR' else 'error',
                'msg': msg,
            }
            self.ws.send(json.dumps(data))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class RedirectOutput(object):
    """重定向标准输出"""
    
    def __init__(self, socket=None):
        self.terminal = sys.stdout
        self.ws = socket

    def update_ws(self, socket=None):
        self.ws = socket
        
    def write(self, output_stream):
        self.terminal.write(output_stream)
        if self.ws is None or self.ws.closed:
            return
        if output_stream in ("\n", "\r", "\t"):
            return
        data = {
            'type': 'output',
            'msg': output_stream,
        }
        self.ws.send(json.dumps(data))
        
    def flush(self):
        pass
        
    def reset(self):
        pass


class SocketMiddleware(object):

    def __init__(self, wsgi_app, socket):
        self.ws = socket
        self.app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if path in self.ws.url_map:
            handler = self.ws.url_map[path]
            environment = environ['wsgi.websocket']
            try:
                handler(environment)
            except geventwebsocket.WebSocketError as e:
                print e
            return []
        else:
            return self.app(environ, start_response)


class Sockets(object):

    def __init__(self, app=None):
        self.url_map = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.wsgi_app = SocketMiddleware(app.wsgi_app, self)

    def route(self, rule, **options):

        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, _, f, **options):
        self.url_map[rule] = f


class WebSockrtLogMaker(object):
    """websocket日志监听生成器

    用于处理日志数据量输出至websocket
    """

    def __init__(self, logger_name, socket=None):
        global _logger
        if _logger is None:
            _logger = logging.getLogger(logger_name)
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(logging.StreamHandler())
        self.wslh = WebSocketsLogHandler(socket)
        _logger.addHandler(self.wslh)
    
    def update_ws(self, socket):
        self.wslh.update_ws(socket)


def make_server(host, port, app=None, request_handler=None):
    """创建wsgi服务和websocket服务"""
    return WSGIServer((host, port), app, handler_class=request_handler)


def run_server(hostname, port, application, use_reloader=False,
               reloader_interval=1, static_files=None,
               request_handler=WebSocketHandler):
    """"运行服务器"""
    import werkzeug
    from werkzeug._internal import _log
    from werkzeug.serving import select_ip_version, socket, run_with_reloader
    
    if static_files:
        from werkzeug.wsgi import SharedDataMiddleware
        application = SharedDataMiddleware(application, static_files)

    def inner():
        make_server(hostname, port, application, request_handler).serve_forever()

    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        display_hostname = hostname != '*' and hostname or 'localhost'
        if ':' in display_hostname:
            display_hostname = '[%s]' % display_hostname
        _log('info', ' * Running on http://%s:%d/',  display_hostname, port)
        if request_handler and hasattr(request_handler, 'run_websocket'):
            _log('info', ' * Running on ws://%s:%d/', display_hostname, port)

    if use_reloader:
        address_family = select_ip_version(hostname, port)
        test_socket = socket.socket(address_family, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind((hostname, port))
        test_socket.close()
        run_with_reloader(inner, None, reloader_interval)
    else:
        inner()
