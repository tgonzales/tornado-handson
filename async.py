import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.escape
import json


url = "https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="

class AsyncHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(url, callback=self.on_fetch)

    def on_fetch(self, response):
        do_something = {}
        do_something['do_something_with_response'] = tornado.escape.json_decode(response.body)
        self.set_header('Content-Type', 'application/json')
        self.write(do_something)
        self.finish()


class GenAsyncHandler(tornado.web.RequestHandler):
    @tornado.web.gen.coroutine
    def get(self):
        response = yield tornado.httpclient.AsyncHTTPClient().fetch(url)
        self.set_header('Content-Type', 'application/json')
        self.write(response.body)

'''
class TestHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        url1 = "https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="
        url2 = "https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="
        http_client = tornado.httpclient.AsyncHTTPClient()        
        http_client.fetch(tornado.httpclient.HTTPRequest(url1, method='GET'), callback=(yield tornado.gen.Callback('k1')))
        http_client.fetch(tornado.httpclient.HTTPRequest(url2, method='GET'), callback=(yield tornado.gen.Callback('k2')))
        response = yield tornado.gen.WaitAll(['k1', 'k2'])

        resp = {}
        resp['k1'] = tornado.escape.json_decode(response[0].body)
        resp['k2'] = tornado.escape.json_decode(response[1].body)
        #for x in response:
        #    resp['result'] = x.body
            #resp[z] = z[z.keys()[0]]
        self.set_header('Content-Type', 'application/json')
        self.write(resp)
        #self.write(response[1].body)
        self.finish()        
'''
class FutureHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        url1 = "https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="
        url2 = "https://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="
        http_client = tornado.httpclient.AsyncHTTPClient()        
        future0 = http_client.fetch(url1)
        future1 = http_client.fetch(url2)
        responses = yield [future0, future1]
        
        resp = {}
        resp['k1'] = tornado.escape.json_decode(responses[0].body)
        resp['k1'] = tornado.escape.json_decode(responses[1].body)

        self.set_header('Content-Type', 'application/json')
        self.write(resp)
    
application = tornado.web.Application([
    (r"/gen", GenAsyncHandler),
    (r"/async", AsyncHandler),
    (r"/stuff/", FutureHandler),

])

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(9999)
tornado.ioloop.IOLoop.instance().start()