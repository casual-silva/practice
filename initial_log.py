#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

try:
    import config
except ImportError:
    sys.path[0] = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
    import config

def _init_logger(filename='spider_' + datetime.datetime.now().strftime("%Y-%m-%d_%H") + ".log", getLogger=__name__):
    '''
    :param filename: such as 'spider_' + datetime.datetime.now().strftime("%Y-%m-%d_%H") + ".log")
    :param getLogger: __name__
    :return: logger
    '''
    logger = logging.getLogger(getLogger)
    if not os.path.isdir(config.LOGDIR):
        os.makedirs(config.LOGDIR)
    logger.setLevel(logging.DEBUG)
    _handler = RotatingFileHandler(filename=os.path.join(config.LOGDIR, filename), mode='a+')
    _handler.setFormatter(logging.Formatter(fmt='>>> %(asctime)-10s %(name)-12s %(levelname)-8s %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(_handler)
    # 控制台输出
    _console = logging.StreamHandler()
    logger.addHandler(_console)
    return logger

if __name__ == '__main__':
    # 自定义日志工具
    logger = _init_logger()

    # 使用原有日志工具
    sys.__APP_LOG__ = False  # 若不使用原有日志工具则在头文件设置 __APP_LOG__ 为Fasle 不进行日志初始化
    print config.APP_LOG
    config.LOG.info(1321)




# sss