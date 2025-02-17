from peewee import PostgresqlDatabase
from decouple import config

# Подключение к PostgreSQL
database = PostgresqlDatabase(
    config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASSWORD'),
    host=config('DB_HOST'),
    port=5432
)
