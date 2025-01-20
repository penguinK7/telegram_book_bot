import os
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from collections import defaultdict
from create_bot import bot  

start_router = Router()

# Словарь для хранения книг и голосов
books = defaultdict(int)

# Добавляем переменную CHAT_ID
CHAT_ID = os.getenv("CHAT_ID")

# Определяем состояния
class Form(StatesGroup):
    waiting_for_book = State()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Используйте /new_book для добавления книги.')

@start_router.message(Command('new_book'))
async def cmd_new_book(message: Message, state: FSMContext):
    await message.answer('Введите название и автора книги в формате "Название - Автор".')
    await state.set_state(Form.waiting_for_book)  # Устанавливаем состояние ожидания для ввода книги

@start_router.message(Form.waiting_for_book)
async def process_new_book(message: Message, state: FSMContext):
    if len(message.text.split(' - ')) == 2:
        title, author = message.text.split(' - ')
        books[f"{title.strip()} - {author.strip()}"] += 0  # Инициализируем книгу с 0 голосами
        await message.answer(f'Книга добавлена: {title.strip()} - {author.strip()}')
    else:
        await message.answer('Пожалуйста, используйте формат: Название - Автор.')

    await state.clear()  # Очищаем состояние после обработки

@start_router.message(Command('vote'))
async def cmd_vote(message: Message):
    if not books:
        await message.answer('Нет доступных книг для голосования.')
        return

    # Создаем клавиатуру с кнопками
    inline_keyboard = []
    for book in books.keys():        
        button_text = book  
        inline_keyboard.append([InlineKeyboardButton(text=button_text, callback_data=book)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)  

    await message.answer('Выберите книгу для голосования:', reply_markup=keyboard)

@start_router.callback_query(F.data)
async def process_vote(callback_query: Message):
    book_title = callback_query.data
    books[book_title] += 1  # Увеличиваем количество голосов для выбранной книги
    await callback_query.answer(f'Вы проголосовали за: {book_title}')

@start_router.message(Command('result'))
async def cmd_result(message: Message):
    if not books:
        await message.answer('Нет книг для отображения результатов.')
        return

    # Определяем победителя
    max_votes = max(books.values())
    winners = [book for book, votes in books.items() if votes == max_votes]

    if len(winners) == 1:
        await message.answer(f'Победила книга: {winners[0]} с {max_votes} голосом(ами).')
    else:
        winners_list = ' и '.join(winners)
        await message.answer(f'Победили книги: {winners_list} с {max_votes} голосом(ами).')