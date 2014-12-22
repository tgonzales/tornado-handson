import tornado.ioloop
import tornado.web
import urllib.request
 
class AsyncHandler(tornado.web.RequestHandler):
        @tornado.web.asynchronous
        def get(self):
                self.response = urllib.request.urlopen("http://www.pythonclub.com.br")
                self._async_callback(self.response)
 
        def _async_callback(self, response):
                print(response.status)
                self.write(str(response.status))
                self.finish()
                tornado.ioloop.IOLoop.instance().stop()
 
application = tornado.web.Application([
        (r"/", AsyncHandler)], debug=True)
 
if __name__ == "__main__":
    application.listen(9999)
    tornado.ioloop.IOLoop.instance().start()