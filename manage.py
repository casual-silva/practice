# -*- encoding: utf-8 -*-

"""HQCHIP接口调试管理及WSGI入口文件

提供接口调试简单运行及 WSGI 入口应用服务

部署运行说明：
    1、开发调试可以直接使用 -d 参数运行，调试模式仅作为开发环境使用，不可用于生产环境部署
    2、简单运行即不使用 -d 会使用 gevent.wsgi 服务，相对直接使用 werkzeug 性能优异很多
    3、生产环境部署，可使用 gunicorn 或者 uwsgi 
        gunicron 可使用使用命令行  gunicorn -w 4 -k gevent -b 127.0.0.1:8787 manage 快速运行，可选自动重载参数 --reload
        uwsgi 须指定配置文件 uwsgi.ini 文件，使用 uwsgi --ini hqchipapi.ini 
    
    * 生产环境推荐 使用 supervisor 进行进程监控守护
"""

__author__ = "qaulau"


import os
import sys
import argparse

os.environ.setdefault('HQCHIP_SETTINGS_MODULE', 'api.config')


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-h', '--help', dest='help', help='获取帮助信息',
                        action='store_true', default=False)
    parser.add_argument('-d', '--debug', dest='debug', help='调试模式，\
                        出错自动重载及完整错误信息，默认 False',
                        action='store_true', default=False)
    parser.add_argument('-r', '--reload', dest='auto_reload', help='自动重载，' \
                        '出错或者代码更新自动重载默认False', action='store_true', 
                        default=False)
    parser.add_argument('-p', '--port', dest='port', help='指定绑定端口，默认为 9090',
                        default=9090, type=int)
    parser.add_argument('-b', '--host', dest='host', help='指定绑定地址，默认为 127.0.0.1',
                        default=None)

    args = parser.parse_args()
    if args.help:
        parser.print_help()
        print("\n示例")
        print(' 指定绑定端口            %s -p 80' % sys.argv[0])
        print(' 指定绑定地址为所有地址  %s --host 0.0.0.0 --port 80' % sys.argv[0])
        print('')
    else:
        from api import make_app
        app = make_app()
        if args.debug:
            app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
        else:
            from gevent import pywsgi
            import werkzeug.serving

            def run_wsgi_server():
                if args.host is None:
                    args.host = '127.0.0.1'
                print('* Running on http://{0}:{1}/ (Press CTRL+C to quit)'.format(args.host, args.port))
                server = pywsgi.WSGIServer((args.host, args.port), app)
                server.serve_forever()
            # 自动重载
            if args.auto_reload:
                run_wsgi_server = werkzeug.serving.run_with_reloader(run_wsgi_server)
            run_wsgi_server()


if __name__ == '__main__':
    main()
else:
    from api import make_app
    application = make_app()
    # from  api.controller import order
