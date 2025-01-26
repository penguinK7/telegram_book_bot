# from peewee import *
# from decouple import config
# import datetime

# # Подключение к PostgreSQL
# database = PostgresqlDatabase(
#     config('DB_NAME'),
#     user=config('DB_USER'),
#     password=config('DB_PASSWORD'),
#     host=config('DB_HOST'),
#     port=5432  # Убедитесь, что порт указан правильно
# )

# class BaseModel(Model):
#     class Meta:
#         database = database

# class User(BaseModel):
#     user_id = BigIntegerField(unique=True)
#     username = CharField(null=True)
#     is_admin = BooleanField(default=False)
#     created_at = DateTimeField(default=datetime.datetime.now)

# class Book(BaseModel):
#     title = CharField()
#     author = CharField()
#     user = ForeignKeyField(User, backref='books')
#     votes = IntegerField(default=0)
#     created_at = DateTimeField(default=datetime.datetime.now)
#     is_active = BooleanField(default=True)

# class Vote(BaseModel):
#     user = ForeignKeyField(User, backref='votes')
#     book = ForeignKeyField(Book, backref='votes')
#     created_at = DateTimeField(default=datetime.datetime.now)

# # Создание таблиц
# def create_tables():
#     # Убедитесь, что база данных подключена
#     database.connect()
#     database.create_tables([User, Book, Vote], safe=True)
#     database.close()