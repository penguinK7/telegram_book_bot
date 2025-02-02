from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from create_bot import bot, scheduler, admins
from db_handler.models import User, Book, Vote
from handlers.decorators import admin_required
from peewee import fn
import random
import datetime
from datetime import timedelta

start_router = Router()

class Form(StatesGroup):
    waiting_for_book = State()
    waiting_for_rating = State()


async def register_user(user_id: int, username: str = None):
    # Используем метод get на модели User с обработкой исключения
    try:
        user = User.get(User.user_id == user_id)
        return user
    except User.DoesNotExist:
        # Если пользователь не найден, создаем нового
        user = User.create(
            user_id=user_id,
            is_admin=user_id in admins,
            username=username
        )
        return user

@start_router.message(CommandStart())
@admin_required
async def cmd_start(message: Message):
    user = await register_user(message.from_user.id, message.from_user.username)
    await clear_database(message)
    await message.answer(
        "📚 Добро пожаловать в Книжный Клуб!\n\n"
        "Доступные команды:\n"
        "/new_book - добавить книгу\n"
        "/vote - начать голосование\n"
        "/random - случайная книга\n"
        "/result - результаты\n"        
    )

@start_router.message(Command('new_book'))
async def cmd_new_book(message: Message, state: FSMContext):
    user = await register_user(message.from_user.id)
    
    existing_book = Book.select().where(Book.user == user).count()  # Уберите await
    if existing_book > 0:
        return await message.answer("❌ Вы уже добавили книгу!")
    
    await message.answer("📖 Введите название и автора в формате:\n\n<code>Название - Автор</code>")
    await state.set_state(Form.waiting_for_book)
    await state.update_data(user_id=user.user_id) 


@start_router.message(Form.waiting_for_book)
async def process_book(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']  # Получаем user_id из состояния
    
    if ' - ' not in message.text:
        return await message.answer("❌ Неверный формат! Пример:\n<code>Война и мир - Лев Толстой</code>")
    
    title, author = message.text.split(' - ', 1)
    
    user = User.get(User.user_id == user_id)  # Получаем объект User по user_id
    Book.create(title=title.strip(), author=author.strip(), user=user)  # Уберите await
    await message.answer(f"✅ Книга добавлена:\n\n<b>{title.strip()}</b>\nАвтор: {author.strip()}")
    await state.clear()

 

@start_router.message(Command('vote'))
@admin_required
async def cmd_vote(message: Message):
    books = Book.select().where(Book.is_active == True)  # Уберите await
    
    builder = InlineKeyboardBuilder()
    for book in books:
        builder.button(text=f"{book.title} - {book.author}", callback_data=f"vote_{book.id}")
    
    builder.button(text="Проголосовать ✅", callback_data="submit_vote")
    builder.adjust(1)
    
    await message.answer(
        "🗳 <b>Голосование началось!</b>\nВыберите книги:",
        reply_markup=builder.as_markup()
    )
    
    scheduler.add_job(
        finish_voting,
        'date',
        run_date=datetime.datetime.now() + timedelta(days=3),
        args=[message.chat.id]
    )
    

@start_router.callback_query(F.data.startswith("vote_"))
async def process_vote(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    user = await register_user(callback.from_user.id)
    
    # Проверяем, голосовал ли пользователь за эту книгу
    vote_exists = Vote.select().where((Vote.user == user) & (Vote.book == book_id)).exists()
    if vote_exists:
        return await callback.answer("❌ Вы уже голосовали за эту книгу!")
    
    # Создаем новый голос
    Vote.create(user=user, book=book_id)  # Убедитесь, что здесь правильный объект Book
    
    # Обновляем количество голосов
    Book.update(votes=fn.Coalesce(Book.votes, 0) + 1).where(Book.id == book_id).execute()  # Используйте fn.Coalesce
    
    await callback.answer("✅ Голос учтён!")
   

async def finish_voting(chat_id: int):
    books = await Book.select().where(Book.is_active == True).order_by(Book.votes.desc()).execute()
    
    max_votes = books[0].votes if books else 0
    winners = [book for book in books if book.votes == max_votes]
    
    text = "🏆 Победители:\n" + "\n".join(
        [f"• {book.title} - {book.author} ({book.votes} гол.)" for book in winners]
    ) if len(winners) > 1 else f"🏆 Победитель: {winners[0].title} - {winners[0].author} ({max_votes} гол.)"
    
    await bot.send_message(chat_id, text)
    await Book.update(is_active=False).execute()

@start_router.message(Command('random'))
@admin_required
async def cmd_random(message: Message):
    books = Book.select().where(Book.is_active == True)  # Уберите await
    
    if not books:
        return await message.answer("📚 Список книг пуст!")
    
    random_book = random.choice(books)
    await message.answer(f"🎲 Случайная книга:\n\n<b>{random_book.title}</b>\nАвтор: {random_book.author}")

@start_router.message(Command('result'))
@admin_required
async def cmd_result(message: Message):
    books = Book.select().order_by(Book.votes.desc())  # Убедитесь, что вы используете правильный синтаксис
    
    # Формируем текст для отправки
    if not books:
        await message.answer("📊 Нет доступных книг для голосования.")
        return
    
    text = "📊 Результаты голосования:\n\n" + "\n".join(
        [f"{i + 1}. {book.title} - {book.author}: {book.votes} гол." 
         for i, book in enumerate(books)]
    )
    await message.answer(text)

@start_router.message(Command('clear'))
@admin_required
async def cmd_clear(message: Message):
    Vote.delete().execute() 
    Book.delete().execute()  
    
    # await message.answer("✅ Все книги и голосования были удалены. Вы можете заново вводить книги и голосовать.")   
    
async def clear_database(message: Message):
    await cmd_clear(message)
