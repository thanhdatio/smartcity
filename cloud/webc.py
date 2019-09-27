#!/usr/bin/python3

from tornado import ioloop, web
from tornado.options import define, options, parse_command_line
from search import SearchHandler
from hint import HintHandler
from redirect import RedirectHandler
from stats import StatsHandler
from subprocess import Popen
from signal import signal, SIGTERM, SIGQUIT

tornadoc=None
nginxc=None

def setup_nginx_resolver():
    with open("/etc/resolv.conf","rt") as fd:
        for line in fd:
            if not line.startswith("nameserver"): continue
            with open("/etc/nginx/resolver.conf","wt") as fdr:
                fdr.write("resolver "+line.strip().split(" ")[1]+";")
            return

def quit_service(signum, frame):
    if tornadoc: tornadoc.add_callback(tornadoc.stop)
    if nginxc: nginxc.send_signal(SIGQUIT)
        
app = web.Application([
    (r'/api/search',SearchHandler),
    (r'/api/stats',StatsHandler),
    (r'/api/workload',RedirectHandler),
    (r'/api/hint',HintHandler),
    (r'/recording/.*',RedirectHandler),
])

if __name__ == "__main__":
    signal(SIGTERM, quit_service)

    define("port", default=2222, help="the binding port", type=int)
    define("ip", default="127.0.0.1", help="the binding ip")
    parse_command_line()
    print("Listening to " + options.ip + ":" + str(options.port))
    app.listen(options.port, address=options.ip)

    tornadoc=ioloop.IOLoop.instance();
    setup_nginx_resolver()
    nginxc=Popen(["/usr/sbin/nginx"])
    tornadoc.start()
    nginxc.wait()
