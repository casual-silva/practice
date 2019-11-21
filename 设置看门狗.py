
def wait_time_out():
    '''看门狗主功能'''
    global call_code
    command = 'taskkill /f /t /IM clicker.exe'
    begin_time = time.time()
    while True:
        if call_code == 0:
            call_code = 1
            return
        wait_time = time.time() - begin_time
        if wait_time >= 120:
            break
    result = subprocess.check_output('tasklist', shell=True)
    if 'clicker.exe' in result and call_code != 0:
        result = subprocess.Popen(command)
        init_proxy()
        close_ie()
        return


def test():
    start_time = int(time.time())
    while True:
        try:
            wait_load_time = 0
            open_ie()
            logger.debug(u"wait page reload {0}s".format(wait_load_time + 2))
            time.sleep(wait_load_time + 2 + 10)
            # 启动广告点击脚本
            global call_code
            # 设置看门狗，超时关闭clicker程序
            # 在程序中值入一个一直存在的线程进行 异常判断, True | 死锁则重启程序
            watch_dog = threading.Thread(target=wait_time_out)
            watch_dog.start()
            call_code = subprocess.call(clicker_path)
            time.sleep(300)
            close_ie()
        except Exception as e:
            print e