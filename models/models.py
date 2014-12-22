from peewee import *
from datetime import datetime

sqlite_db= SqliteDatabase('people.db')
psql_db = PostgresqlDatabase('my_database', user='postgres', password='secret')
# back to a local Sqlite database if no database URL is specified.
#db = connect(os.environ.get('DATABASE') or 'sqlite:///default.db')

class BaseModel(Model):
    class Meta:
        database = sqlite_db

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    join_date = DateTimeField(default=datetime.now)

    class Meta:
        order_by = ('username',)


def create_tables():
    db.connect()
    db.create_tables([User])

'''
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

'''

