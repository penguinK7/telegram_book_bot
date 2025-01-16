import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram import F
from dotenv import load_dotenv
import asyncio

# Загрузка переменных окружения из .env файла
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

router = Router()

# Определение состояний
class Form(StatesGroup):
    waiting_for_book = State()

# Обработка команды /start
@router.message(F.command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Используйте /new_book для добавления книги.")

# Команда /new_book
@router.message(F.command('new_book'))
async def cmd_new_book(message: types.Message):
    await Form.waiting_for_book.set()
    await message.answer("Пожалуйста, введите название и автора книги в формате 'Название - Автор'.")

# Обработка ожидания ввода книги
@router.message(Form.waiting_for_book)
async def process_book(message: types.Message, state: State):
    book_info = message.text
    await message.answer(f"Вы добавили книгу: {book_info}новик ")
    # Здесь можно добавить код для сохранения книги в БД или в файл
    await state.clear()  # Очистка состояния

# Запуск бота
async def main():
    dp.include_router(router)  # Включаем роутер
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())