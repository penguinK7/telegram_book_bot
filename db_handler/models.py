from peewee import Model, BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField, IntegerField
import datetime
from db_handler.db_class import database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    user_id = BigIntegerField(unique=True)
    username = CharField(null=True)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)


class Book(BaseModel):
    title = CharField()
    author = CharField()
    user = ForeignKeyField(User, backref='books')
    votes = IntegerField(default=0)  
    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)


class Vote(BaseModel):
    user = ForeignKeyField(User, backref='votes')
    book = ForeignKeyField(Book, backref='votes')
    created_at = DateTimeField(default=datetime.datetime.now)
