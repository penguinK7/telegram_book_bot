import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
# from peewee import PostgresqlDatabase

# Инициализация Redis
redis = Redis.from_url(config('REDIS_URL'))

# Инициализация бота
bot = Bot(
    token=config('TOKEN'),
    default=DefaultBotProperties(parse_mode="HTML")
)

# Настройка хранилища состояний
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)

# Планировщик задач
scheduler = AsyncIOScheduler()

# Список админов
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

# Логирование
logging.basicConfig(level=logging.INFO)

# Подключение к PostgreSQL
# database = PostgresqlDatabase(
#     config('DB_NAME'),
#     user=config('DB_USER'),
#     password=config('DB_PASSWORD'),
#     host=config('DB_HOST')
# )