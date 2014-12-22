import tornado.web
from models.models import User

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")	

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render('main.html')


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        user = User.get(User.username == username)
        if user.username == username and user.password == password:
            self.set_secure_cookie("user", username)
            self.redirect("/")
        else:
            self.set_status(403)
            self.write_error(403)

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.write({'User Token':'Has been Deleted'})
