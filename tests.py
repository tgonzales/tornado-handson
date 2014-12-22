import urllib.request
import urllib.parse
import unittest

class TestTornadoHandlers(unittest.TestCase):
    def test_home(self):
        url = urllib.request.urlopen('http://localhost:8888')
        self.assertEqual(url.status, 200)

    def test_login_get(self):
        url = urllib.request.urlopen('http://localhost:8888/login')
        self.assertEqual(url.status, 200)

    def test_login_post(self):
        data = urllib.parse.urlencode({'username': 'demo', 'password': 'demo'})
        data = data.encode('utf-8')
        request = urllib.request.Request("http://localhost:8888/login")
        request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        url = urllib.request.urlopen(request, data)
        self.assertEqual(url.status, 200)

if __name__ == '__main__':
    unittest.main()