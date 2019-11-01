import os, datetime, logging
from logging.handlers import RotatingFileHandler

'''
日志配置
'''
APP_LOG = getattr(sys,'__APP_LOG__',True)
level = logging.DEBUG if DEBUG else logging.ERROR
LOGDIR = os.path.join(APP_ROOT, "logs")
#仅应用日志
if APP_LOG:
    #每小时一个日志
    _handler = RotatingFileHandler(filename = os.path.join(LOGDIR, 'spider_' + datetime.datetime.now().strftime("%Y-%m-%d_%H") + ".log"),mode = 'a+')
    _handler.setFormatter(logging.Formatter(fmt = '>>> %(asctime)-10s %(name)-12s %(levelname)-8s %(message)s',datefmt ='%H:%M:%S'))
    LOG = logging.getLogger('hqchip_spider')
    LOG.setLevel(level)
    LOG.addHandler(_handler)
    #在控制台打印
    _console = logging.StreamHandler()
    LOG.addHandler(_console)