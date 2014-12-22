Hand's On Tornado Web
=====================

Criado pelo pessoal do FriendFeed foi tornado open source pelo Facebook. Podemos dizer que o Tornado é 2 em 1, micro framework e webserver. É mais conhecido pelo seu potencial performático assíncrono, robusto e escalável, é uma ótimo alternativa ao WSGI, que é uma interface fantástica mas que possui limitações (assunto para outro post). Algumas características importantes

- É um framework bonitinho, mas não somente.
- Escala mantendo um baixo consumo de CPU e Memória
- É python puro, roda com python 3.4 e Pypy
- Tem uma grande variedade de conectores async para Tornado.
- Suporte a Non-blocking I/O e Websockets
- Extremamente fácil subir instancias e fazer um proxy reverso com Nginx.

Mas com o alto poder de seu HTTP Server o micro-framework acabe ficando escondidinho, mas confesso que depois de utiliza-lo em alguns projetos em produção posso dizer que o Tornado oferece um excelente framework mesmo quando não existe uma necessidade assíncrona.

A sua documentação oficial (recomendo a sua leitura) nos brinda um Hello World, desta maneira::

  import tornado.ioloop
  import tornado.web

  class MainHandler(tornado.web.RequestHandler):
      def get(self):
          self.write("Hello, world")

  application = tornado.web.Application([
      (r"/", MainHandler),
  ])

  if __name__ == "__main__":
      application.listen(8888)
      tornado.ioloop.IOLoop.instance().start()


Em nosso simples Hello World, podemos identificar:

**tornado.web.RequestHandler**, classe Tornado responsável por receber o request e retornar o resultado.

**tornado.web.Application**, classe Tornado que encapsula a aplicação, nesse exemplo temos uma lista das urls e seus respectivos Handlers

**application.listen(8888)**, bem auto-explicativo, nossa aplicação será executada na porta 8888

**tornado.ioloop.IOLoop.instance().start()**, o server tornado em ação, cria uma instancia de nossa aplicação na porta 8888 e inicia.::

  curl http://localhost:8888
  Hello World

Para dar um stop no server, Ctrl + C.


Objetivo desse Hand's On
------------------------

- Explicar o básico sobre o funcionamento do Tornado Web
- Desenvolver uma aplicação completa usando Tornado como Backend, AngularJS com frontend e Motor (um conector assíncrono para tornado e mongodb).

**Roteiro**

1. Instalação
2. Modularizando a Aplicação
3. Models - Fazendo uma conexão com banco de dados
4. Enviando Formulário, cookie, login e logout.
5. Async Handler
6. WebSocket
7. Criando a Aplicação frontend
8. Criando a Aplicação backtend


1. Instalação
-------------
::

  mkdir handson-tornado && cd handson-tornado
  pyenv virtualenv handson-tornado
  pyenv activate handson-tornado
  pip install tornado
  
#vim app.py
  
::

  import tornado.web
  import tornado.ioloop

  class MainHandler(tornado.web.RequestHandler):
      def get(self):
          self.write('Hello Word')

  app = tornado.web.Application([
      (r'/',MainHandler)])

  if __name__ == '__main__':
      app.listen(8888)
      tornado.ioloop.IOLoop.instance().start()

  python app.py
  # em outra tab do console
  curl http://localhost:8888 


Modularizando a Aplicação
-------------------------

Sendo um microframework o tornado permite modularizar sua aplicação da maneira em que seu projeto se enquadre melhor. Como exemplo vamos modularizar seguindo o princípio do MVC, criando pacotes para armazenas nossos controllers, views e models::

  mkdir controllers
  mkdir views
  mkdir models

Para manter a compatibilidade com python 2, adicione __init__.py em cada diretório para que este seja um pacote python. Para usuários do Django pode ser mais conveniente criar um pacote todolist e dentro dele os arquivos views.py, models.py e urls.py, você tem a liberdade de modularizar seu código conforme seu gosto ou especificação do projeto. Da mesma maneira o pacote views poderá ser chamado de templates.

**Definindo nossos Controllers (C de MVC)**::

  #vim controllers/handlers.py
  import tornado.web

  class MainHandler(tornado.web.RequestHandler):
      def get(self):
          self.write('Hello Word')

Alterando nossa app.py para acessar os Handlers dentro de controllers
import controllers.handlers::

  app = tornado.web.Application([
      (r'/', controllers.handlers.MainHandler),
  ])

Você também poderá usar::

  form controllers.handlers import MainHandler

  app = tornado.web.Application([(r'/', MainHandler)])

#vim views/main.html.::

  <html>
  <head>
        <title>Hand's on Tornado</title>
  </head>
  <body>
  <h1>Hello Tornado!</h1>
  </body>
  </html>

Alterando nosso MainHandler::

  class MainHandler(tornado.web.RequestHandler):
      def get(self):
          #self.write('Hello Word')
          self.render('../views/templates/main.html')

Antes de criar nosso modelo, vamos extender nossa applicação, app = tornado.web.Application(), criando uma classe Application para adicionar mais configurações.::

  import tornado.httpserver
  import os

  class App(tornado.web.Application):
      def __init__(self):
          handlers = [
              (r'/', controllers.handlers.MainHandler),
          ]
          settings = dict(
            debug = True,
            template_path = os.path.join(base_dir, "views"),
          )
          tornado.web.Application.__init__(self, handlers, **settings)

  if __name__ == '__main__':
     http_server = tornado.httpserver.HTTPServer(App())
     http_server.listen(8888)
     tornado.ioloop.IOLoop.instance().start()

Transformamos nossa variável app em um Classe que instancia os handlers e settings, na settings colocamos template_path com o nosso diretório dos templates, em breve adicionaremos mais informações nessa settings. Uma boa prática seria criar um diretório template e static dentro de views.::

  template_path = os.path.join(base_dir, "views/templates"),
  static_path = os.path.join(base_dir, "views/statics"),

Também instanciamos "tornado.httpserver" para servir nossa classe App.

Módulo Define.
O Tornado possui um módulo chamado "define" que permite adicionar namespaces globais.::

  form tornado.options import define, options
  define("port", default=8888, help="run on the given port", type=int)

  http_server.listen(options.port)

agora podemos usar a flag --port para instanciarmos nossa aplicação::

  python app.py --port=9000

senão adicionarmos essa flag a porta default fica sendo a 8888 como especificado em define. Portanto, fazer um proxy reverso com Nginx é muito simples.::

  python app.py --port=9000
  python app.py --port=9001
  python app.py --port=9002
  python app.py --port=9003

  #nginx
  127.0.0.1:9000
  127.0.0.1:9001
  127.0.0.1:9002
  127.0.0.1:9003

Enviando Formulário, cookie, login e logout.
--------------------------------------------
**Definindo nosso Models (M de MVC)**

Vamos utilizar um ORM muito interessante chamado peewee, uma outra alternativa seria SQLAlchemy, muito utilizado com flask, bottle e web2py.::

  #vim models/models.py
  from peewee import *

  sqlite_db= SqliteDatabase('people.db')

  class BaseModel(Model):
      class Meta:
          database = sqlite_db

  class User(BaseModel):
      username = CharField(unique=True)
      password = CharField()
      email = CharField()
      join_date = DateTimeField(default=datetime.datetime.now)

      class Meta:
          order_by = ('username',)

  def create_tables():
      db.connect()
      db.create_tables([User])

Definimos um Model base (BaseModel) que irá conter os atributos a serem utilizados por todos os nossos modelos, database da Classe Meta define que todos os nossos modelos que herdam de BaseModel irá conectar o sqlite3.
Vamos interagir com a API do Peewee.::

  > python
  >>> from models.models import create_tables, User
  >>> from datetime import datetime
  >>> create_tables()
  >>> user = User(username='Bob', password='1234', email='bob@bob.com')
  >>> user.save()
  >>> user.username
  'Bob'
  >>> bob = User.get(User.username == 'Bob')
  >>> User.select()
  >>> query = User.select().where(User.username == 'Bob')
  >>> for user in query:
  ...    print(user.email)
  ... 
  bob@bob.com

**Testes Unitários**::

  #vim tests.py
  import urllib.request
  import unittest

  class TestSequenceFunctions(unittest.TestCase):
      def test_home(self):
          url = urllib.request.urlopen('http://localhost:8888')
          self.assertEqual(url.status, 200)

  if __name__ == '__main__':
      unittest.main()

  $ python -m unittest tests
  ----------------------------------------------------------------------
  Ran 1 test in 0.005s

  OK

  Nosso teste passou!!

**Criando um formulário para login com Tornado**

Vamos criar primeiro o test unitário, adicionando um novo método test_login para validar o status code de get e post::

  #vim tests.py
  #ADD Class test_login_get e test_login_post dentro de class TestTornadoHandlers()
  def test_login_get(self):
      url = urllib.request.urlopen('http://localhost:8888/login')
      self.assertEqual(url.status, 200)

  def test_login_post(self):
      data = urllib.parse.urlencode({'username': 'test', 'password': 'test'})
      data = data.encode('utf-8')
      request = urllib.request.Request("http://localhost:8888/login")
      request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
      url = urllib.request.urlopen(request, data)
      self.assertEqual(url.status, 200)

  $ python -m unittest tests
  ----------------------------------------------------------------------
  Ran 3 tests in 0.049s

  FAILED (errors=2)

  Falhou, isso era o esperado, vamos usar TDD, sempre criando testes antes da implementação

**Controllers**::

  vim controllers/handlers.py
  class LoginHandler(BaseAuthHandler):
      def get(self):
            self.render('login.html')

      def post(self):
            self.write('Method Post in Action')

**Views**::

  #vim views/templates/login.html
  {% block content %}
  <form action="" method="post">
    <input type="text" name="username">
    <input type="password" name="password">
    <input type="submit" value="login">
  </form>
  {% end block %}

  #vim views/templates/login.html
  {% block content %}
  <h1>Hello Tornado</h1>
  {% end block %}

A linguagem de template do Tornado é bem semelhante ao Django Templates e Jinja2. Em main.html adicionamos a tag block content, em login.html substituimos o conteúdo do block content pelo formulário de login.::

  #vim app.py
  handlers = [
    (r'/', controllers.handlers.MainHandler),
    (r'/login', controllers.handlers.LoginHandler),
  ]

Adicionamos nosso LoginHandler à url '/login'.::

  $ python -m unittest tests
  #passou? siga em frente...

  $ python app.py
  # no browser: http://localhost:8888/login

**Validando o form**
Vamos substituir o nosso método POST do handler LoginHandler fazendo uma autenticação muito simples.::

  def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        if "demo" == username and "demo" == password:
            self.write('Method Post in Action')
        else:
            self.set_status(403)
            self.write_error(403)

  $ python -m unittest tests

  urllib.error.HTTPError: HTTP Error 403: Forbidden
  --------------------------------------------------------------------
  Ran 3 tests in 0.012s

  FAILED (errors=1)

Falhou porque o user/senha do teste não é a esperada pelo backend.

**Autenticando o user no banco de dados.**
Como ja haviamos definido o nosso models, podera agora validar user e senha no banco. Uma maneira bem simples de fazer isso, seria::

  #vim controllers/handlers
  from models.models import User

  #Alteramos nosso método POST de LoginHandler
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        user = User.get(User.username == username)

        if user.username == username and user.password == password:
            self.write('Method Post in Action - {0}'.format(user.username))
        else:
            self.set_status(403)
            self.write_error(403)

**Autenticação com cookies**
O Tornado possui um módulo de autenticação disponível em self.current_user, e nos templates current_user, o default is None. Para certificar disso, basta colocar a tag em algum template.::

  user: {{ current_user }}

O primeiro passo seria subscrever essa classe self.current_user para checarmos se o user tem um cookie de sessão criado. Mas antes é necessário adicionar alguns valores na settings da aplicação::

  #vim app.py
  settings = dict(
    debug=True,
    template_path = os.path.join(base_dir, "views/templates"),
    cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    login_url= "/login",
  )

O parâmetro login_url nos permite user o método self.redirect(), ex. if not self.current_user: self.redirect(). O parâmetro cookie_secret é a chave de segurança para deixar nossos formulários protegidos. Precisamos gerar essa chave única.::

  $ python
  >>>import uuid
  >>>get_security_key = uuid.uuid4().hex
  >>> get_security_key
  '1d7e5627ed07425aa0d8829628c6a284'
  Basta adicionar a chave gerada em cookie_secret.

  #vim controllers/handlers.py
  class BaseHandler(tornado.web.RequestHandler):
      def get_current_user(self):
          return self.get_secure_cookie("user")

Criamos um classe BaseHandler que verifica se o user tem cookie, e todas as demais classes passam a herdar delas, class MainHandler(BaseHandler), LoginHandler(BaseHandler), etc...

Vamos verificar se o user entrou em nossa home (r'/') sem cookie, se isso acontecer vamos redirecionar para login (r'/login').::

  #vim controllers/handlers.py
  class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render('main.html')

No método POST de LoginHandler, podemos gravar o cookie com o método self.set_secure_cookie, caso o usuário seja válido, depois será redirecionado para home (r'/')::

  if user.username == username and user.password == password:
      self.set_secure_cookie("user", username)
      self.redirect("/")
  else:

Se houver qualquer dúvida, verifique o arquivo completo no github desse hand's on.

Para fechar esse assunto, havia falado anteriormente sobre o parâmetro cookie_secret, mas, acabamos fazendo uma solicitação POST sem proteção e funcionou perfeitamente, o que aconteceu?
Precisamos adicionar um novo parâmetro em nossa settings,::

  cookie_secret="1d7e5627ed07425aa0d8829628c6a284",

Tente enviar o formulário novamente e receberá um raise exception
tornado.web.HTTPError: HTTP 403: Forbidden ('_xsrf' argument missing from POST)

Para projeger contra ataques::

  #vim views/templates/login.html
  <form action="" method="post">
    {% module xsrf_form_html() %}

O tornado também possui um módulo de autenticação utilizando OpenID e OAUTH facebook, twitter, google e friendfeed, mas como é necessário gerar token desses serviços foge do escopo desse hand's on.

Assíncrono e Não Bloqueante.
----------------------------
**No-blocking**

Em sistemas com arquitetura de Threads Bloqueantes quando 10 usuários simultâneos acessam o mesmo recurso, todos eles são enfileirados, fazendo com que cada um deles utilizem esse recurso um de cada vez e o recurso bloqueia o acesso aos demais usuários dando exclusividade apenas o usuário que esta utilizando-o, isso garante integridade nos dados pois há um controle em que todo mundo acessa-o unicamente. Threads Não-Bloqueantes é totalmente o inverso, ou seja, ninguém controla a concorrência de usuários e isso traz como benefício um ganho maior em performance.

Diversos sistemas pode utilizar esse conceito sem prejudicar os usuários, geralmente são sistemas que trabalham mais com consultas na base de dados do que alterações no mesmo. No entanto existe diversas situações onde o sistema deve ser bloqueante, visto que é obrigatório controlar a concorrência de usuários para garantir a integridade dos dados, ex. sistemas bancários e e-commerces. 

**Async**

Os sistemas web convencionais possuem um padrao de request/response, ou seja, enviamos uma solicitação ao servidor (request) que irá tratar essa requisição e retornar os dados esperados (response), já uma chamada assíncrona é baseada em um paradígma orientado a eventos. Evento é um indicador de que algo aconteceu, agora existe um produtor do evento e um consumidor do evento, a diferença básica aqui é que um produtor de evento não espera a ação ser executada (consumidor de evento) para então processar os resultados. Exemplificando o conceito, quando solicitamos uma ação no banco de dados de forma síncrona há a necessidade de esperar o processamento da requisição para a solicitação ser complicada enquanto que na chamada assíncrona a solicitação e agendada (criada um evento) e desbloqueada, podendo assim fazer outras chamadas, quando o eventos estiver processado ele será retornado. Uma consideração importante é que em chamadas assíncronas não existe uma ordem de retorno a não ser a primeira que termina é a primeira que retorna.::

  #http://nichol.as/asynchronous-servers-in-python

  #vim controllers/handlers.py
  url = "https://query.yahooapis.com/v1/public/yql? q=SELECT%20*%20FROM%20search.ec%20(1%2C%2010)%20WHERE%20keyword%3D'ipad'%20and%20property%3D'shopping'%20and%20sortBy%3D'price'%20and%20sortOrder%3D'asc'%20and%20filters%3D'ship_fast'&format=json&diagnostics=true&callback="

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

  #vim app.py
  (r"/async", controllers.handlers.AsyncHandler),

Temos uma url com uma simples consulta na api do yahoo, para a Handler responder de forma assíncrona usamos o decorator ."asynchronous", criamos uma instância de AsyncHTTPClient e adicionamos o callback on_fetch, o AsyncHTTPClient é no-blocking e o callback se encarrega de tratar o response quando ele vier.

**Coroutine**

O tornado possui um módulo de coroutines que permite uma programação assíncrona usando generators eliminando os callbacks. Esse mesmo Handler refatorado para coroutine, seria::

  #vim controllers/handlers.py
  class GenAsyncHandler(tornado.web.RequestHandler):
    @tornado.web.gen.coroutine
    def get(self):
        response = yield tornado.httpclient.AsyncHTTPClient().fetch(url)
        self.set_header('Content-Type', 'application/json')
        self.write(response.body)

  #vim app.py
  (r"/gen", controllers.handlers.GenAsyncHandler),

Consultando duas urls e passando o resultando para a view.::

  class FutureHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()        
        future0 = http_client.fetch(url)
        future1 = http_client.fetch(url)
        responses = yield [future0, future1]
        
        resp = {}
        resp['k1'] = tornado.escape.json_decode(responses[0].body)
        resp['k1'] = tornado.escape.json_decode(responses[1].body)

        self.set_header('Content-Type', 'application/json')
        self.write(resp)

  #vim app.py
  (r"/stuff/", FutureHandler),

**WebSocket**

Tornado possui uma implementação para Websockets, um protocolo de comunicação bidirecional entre o browser e o servidor permitindo a conexão persistente e ambas as partes podem começar a enviar dados a qualquer momento.

Confira um chat demo na documentação oficial do Tornado em:
https://github.com/tornadoweb/tornado/blob/master/demos/websocket/

Uma implementação muito interessante é a socketJs-tornado que usa a lib socketJS uma alternativa ao socketIO. Um chat simples se parece com isso.

#vim ws.py::

  import tornado.ioloop
  import tornado.web
  import sockjs.tornado

  class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('ws.html')

  class ChatConnection(sockjs.tornado.SockJSConnection):
    participants = set()

    def on_open(self, info):
        self.broadcast(self.participants, "Someone joined.")
        self.participants.add(self)

    def on_message(self, message):
        self.broadcast(self.participants, message)

    def on_close(self):
        self.participants.remove(self)
        self.broadcast(self.participants, "Someone left.")

  if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')
    app = tornado.web.Application(
            [(r"/", IndexHandler)] + ChatRouter.urls
    )
    app.listen(5555)
    tornado.ioloop.IOLoop.instance().start() 


#vim ws.html::

  <!DOCTYPE html>
  <html>
  <head>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
    <script src="http://cdn.jsdelivr.net/sockjs/0.3/sockjs.min.js"></script>
    <script>
      $(function() {
        var conn = null;
        function log(msg) {
          var control = $('#log');
          control.html(control.html() + msg + '<br/>');
          control.scrollTop(control.scrollTop() + 1000);
        }
        function connect() {
          disconnect();
          var transports = $('#protocols input:checked').map(function(){
              return $(this).attr('id');
          }).get();
          conn = new SockJS('http://' + window.location.host + '/chat', transports);
          log('Connecting...');
          conn.onopen = function() {
            log('Connected.');
            update_ui();
          };
          conn.onmessage = function(e) {
            log('Received: ' + e.data);
          };
          conn.onclose = function() {
            log('Disconnected.');
            conn = null;
            update_ui();
          };
        }
        function disconnect() {
          if (conn != null) {
            log('Disconnecting...');
            conn.close();
            conn = null;
            update_ui();
          }
        }
        function update_ui() {
          var msg = '';
          if (conn == null || conn.readyState != SockJS.OPEN) {
            $('#status').text('disconnected');
            $('#connect').text('Connect');
          } else {
            $('#status').text('connected (' + conn.protocol + ')');
            $('#connect').text('Disconnect');
          }
        }
        $('#connect').click(function() {
          if (conn == null) {
            connect();
          } else {
            disconnect();
          }
          update_ui();
          return false;
        });
        $('form').submit(function() {
          var text = $('#text').val();
          log('Sending: ' + text);
          conn.send(text);
          $('#text').val('').focus();
          return false;
        });
      });
  </script>
  </head>
  <body>
  <h3>Chat!</h3>
  <div id="protocols" style="float: right">
    <ul>
      <li>
        <input id="websocket" type="checkbox" value="websocket" checked="checked"></input>
        <label for="websocket">websocket</label>
      </li>
      <li>
        <input id="xhr-streaming" type="checkbox" value="xhr-streaming" checked="checked"></input>
        <label for="xhr-streaming">xhr-streaming</label>
      </li>
      <li>
        <input id="iframe-eventsource" type="checkbox" value="iframe-eventsource" checked="checked"></input>
        <label for="iframe-eventsource">iframe-eventsource</label>
      </li>
      <li>
        <input id="iframe-htmlfile" type="checkbox" value="iframe-htmlfile" checked="checked"></input>
        <label for="iframe-htmlfile">iframe-htmlfile</label>
      </li>
      <li>
        <input id="xhr-polling" type="checkbox" value="xhr-polling" checked="checked"></input>
        <label for="xhr-polling">xhr-polling</label>
      </li>
      <li>
        <input id="iframe-xhr-polling" type="checkbox" value="iframe-xhr-polling" checked="checked"></input>
        <label for="iframe-xhr-polling">iframe-xhr-polling</label>
      </li>
      <li>
        <input id="jsonp-polling" type="checkbox" value="jsonp-polling" checked="checked"></input>
        <label for="jsonp-polling">jsonp-polling</label>
      </li>
    </ul>
  </div>

  <div>
    <a id="connect" href="#">Connect</a>&nbsp;|&nbsp;Status: <span id="status">disconnected</span>
  </div>
  <div id="log" style="width: 60em; height: 20em; overflow:auto; border: 1px solid black">
  </div>
  <form id="chatform">
    <input id="text" type="text" />
    <input type="submit" />
  </form>
  </body>
  </html>



Criando a Aplicação frontend
----------------------------

Criando a Aplicação backtend
----------------------------

