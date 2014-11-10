import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)
define("host", default="127.0.0.1:3306", help="blog database host")
define("database", default="blog", help="blog database name")
define("user", default="blog", help="blog database user")
define("password", default="blog", help="blog database password")

from os.path import dirname
import sys
sys.path.append(dirname(__file__))

from handlers.misc import HomeHandler
from handlers.misc import Application

from handlers.odds.handlers import OddsHome
from handlers.odds.handlers import OddsDetail
from handlers.odds.handlers import OddsHistory
from handlers.odds.handlers import OddsNext

from handlers.statistics.handlers import StatisticsHome
from handlers.statistics.handlers import StatisticsList
from handlers.statistics.handlers import StatisticsDetail

handlers = [
    (r"/", HomeHandler),
    (r"/odds/home/*", OddsHome),
    (r"/odds/detail/", OddsDetail),
    (r"/odds/history/", OddsHistory),
    (r"/odds/next/", OddsNext),
    (r"/statistics/home/*", StatisticsHome),
    (r"/statistics/list/", StatisticsList),
    (r"/statistics/detail/", StatisticsDetail),
]

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=True,
    cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    debug=True,
)

def main():
    tornado.options.parse_command_line()
    app = Application(handlers, settings, options)
    if 1:
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
