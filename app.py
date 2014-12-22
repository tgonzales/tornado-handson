import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options

import controllers.handlers

import os

define("port", default=8888, help="run on the given port", type=int)

base_dir = os.path.dirname(__file__)

class App(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r'/', controllers.handlers.MainHandler),
			(r'/login', controllers.handlers.LoginHandler),
		]
		settings = dict(
			debug=True,
			template_path = os.path.join(base_dir, "views/templates"),
			cookie_secret="1d7e5627ed07425aa0d8829628c6a284",
		    login_url= "/login",
            xsrf_cookies= True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(App())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
