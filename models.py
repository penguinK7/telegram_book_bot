from peewee import Model, CharField, IntegerField


class Book(Model):
    title = CharField()
    author = CharField()
    votes = IntegerField(default=0)
