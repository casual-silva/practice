#!/usr/bin/env python
# !encoding=utf-8

import sys, os, time, atexit, string, ConfigParser, commands, subprocess
from signal import SIGTERM

PID_FILE = "./SqyDaemon.pid"
CONFIG_FILE = "SqyDaemon.ini"
SECTION = "Monitor"
SECTION_KEY = "Process"

 


class Daemon:
    def __init__(self, configFile, pidfile):
        self.pidfile = pidfile
        self.configFile = configFile
        cfg = ConfigParser.ConfigParser()
        try:
            cfg.read(self.configFile)
            allprocesses = cfg.get(SECTION, SECTION_KEY)
            if '#' in allprocesses:
                position1 = allprocesses.find('#')
                self.processes = allprocesses[:position1]
            else:
                self.processes = allprocesses
            self.processes = self.processes.strip()
            self.monitorProcess = self.processes.split(',')
        except Exception, e:
            print e

    def _daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # 退出主进程
        except OSError, e:
            print "fork failed!\nError is:", e.strerror
            sys.exit(1)
        os.setsid()
        os.umask(0)
        # 创建子进程
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            print "fork failed!\nError is:", e.strerror
            sys.exit(1)
        # 创建processid文件
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write('%s\n' % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            print "pidfile %s already exist. SqyDaemon already running?\n" % self.pidfile
            sys.exit(1)
        # 启动监控
        self._daemonize()
        self._run()

    def stop(self):
        # 从pid文件中获取pid
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            if "-r" == sys.argv[1]:
                print "SqyDaemon restart and monitor related process!"
            else:
                message = 'pidfile %s does not exist. SqyDaemon not running?\n'
                sys.stderr.write(message % self.pidfile)
            return  # 重启不报错
        elif "-r" == sys.argv[1]:
            print "%s is runing,now restart!" % sys.argv[0]
        elif "-k" == sys.argv[1]:
            print "all processes are killed!"
        # 杀进程
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                for tmpprocees in self.monitorProcess:
                    processname = os.path.basename(tmpprocees)
                    os.system("killall %s" % processname)
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def _run(self):
        while True:
            for tmpprocees in self.monitorProcess:
                processname = os.path.basename(tmpprocees)
                fullpath = os.path.abspath(tmpprocees)
                count = commands.getoutput("ps -elf | grep %s | grep -v %s | wc -l" % (processname, "grep"))
                if 0 == int(count):
                    os.system(tmpprocees + " 1>/dev/null 2>/dev/null &")  # 标准输出和错误输出重定向到/dev/null
                else:
                    continue
            time.sleep(2)


def help():
    print "Usage:"
    print "%s -m 			---monitor all processes" % sys.argv[0]
    print "%s -k 			---kill all processes" % sys.argv[0]
    print "%s -r 			---restart all processes" % sys.argv[0]


if __name__ == '__main__':
    daemon = Daemon(CONFIG_FILE, PID_FILE)
    if len(sys.argv) == 2:
        if '-m' == sys.argv[1]:
            daemon.start()
        elif '-k' == sys.argv[1]:
            daemon.stop()
        elif '-r' == sys.argv[1]:
            daemon.restart()
        else:
            print 'Unknown command'
            help()
            sys.exit(2)
        sys.exit(0)
    else:
        help()
        sys.exit(2)



# ------------------------------------------------
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, os, time, atexit
from signal import SIGTERM


class Daemon(object):
    '''
    守护进程类，所谓守护进程故名思意是为了保护进程使进程可以在后台安全运行
    基本思路是使用一个父进程，然后fork一个子进程，保存子进程的pid，最后退出父进程
    再次运行代码时会根据pid文件进行检查，是否有对应进程在运行，没有的话会新启动，有的话不会新启动进程而是直接退出
    这样即使代码在后台运行，又能保证不会无限的启动进程
	
    Usage: 继承本类并重写 run() 方法
	'''

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        #进行第二次 fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 写入 pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        启动守护进程
        """
        # 检测 pidfile以确认守护进程是否在运行中
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        '''
        停止守护进程
        '''
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)


    def restart(self):
        '''
        重启守护进程
        '''
        self.stop()
        self.start()


    def run(self):
        '''
        在子类中重写这个方法，然后使用 start() 或者 restart() 启动守护进程
        '''
        pass