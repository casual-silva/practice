def date(timestamp=None, format='%Y-%m-%d %H:%M'):
    '''
    时间戳格式化转换日期

    @params
            timestamp ：时间戳，如果为空则显示当前时间
            format : 时间格式

        @return
            返回格式化的时间，默认为 2014-07-30 09:50 这样的形式
        '''
    if timestamp is None:
        timestamp = int(time.time())
    if not isinstance(timestamp, int):
        timestamp = int(timestamp)
    d = datetime.datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def strtotime(string, format="%Y-%m-%d %H:%M"):
    '''
    字符串转时间戳

    @params
        string : 需要转换成时间戳的字符串，需要与后面的format对应
        format : 时间格式

    @return
        返回对应的10位int数值的时间戳
    '''
    try:
        return int(time.mktime(time.strptime(string, format)))
    except Exception:
        return 0


def filter_symbols(text):
    '''
    剔除数字，字母，汉字以外的字符
    :param text:
    :return:
    '''
    rule = re.compile(ur"[^a-zA-Z0-9\u4e00-\u9fa5]")
    text = rule.sub('', text)
    return text