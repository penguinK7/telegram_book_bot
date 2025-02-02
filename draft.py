from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from create_bot import bot, scheduler, admins
from db_handler.db_class import User, Book, Vote
from handlers.decorators import admin_required
import random
import datetime
from datetime import timedelta

start_router = Router()

class Form(StatesGroup):
    waiting_for_book = State()
    waiting_for_rating = State()

# books = []
# votes = {}    

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
async def cmd_start(message: Message):
    user = await register_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "📚 Добро пожаловать в Книжный Клуб!\n\n"
        "Доступные команды:\n"
        "/new_book - добавить книгу\n"
        "/vote - начать голосование\n"
        "/random - случайная книга\n"
        "/result - результаты\n"
        "/clear - очистить список книг"
    )

@start_router.message(Command('new_book'))
async def cmd_new_book(message: Message, state: FSMContext):
    user = await register_user(message.from_user.id)
    
    existing_book = await Book.select().where(Book.user == user).count()
    if existing_book > 0:
        return await message.answer("❌ Вы уже добавили книгу!")
    
    await message.answer("📖 Введите название и автора в формате:\n\n<code>Название - Автор</code>")
    await state.set_state(Form.waiting_for_book)
    await state.update_data(user=user)

# @start_router.message(Command('new_book'))
# async def cmd_new_book(message: Message, state: FSMContext):
#     await message.answer("📖 Введите название и автора в формате: Название книги - Автор книги")
#     await state.set_state(Form.waiting_for_book)    

@start_router.message(Form.waiting_for_book)
async def process_book(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data['user']
    
    if ' - ' not in message.text:
        return await message.answer("❌ Неверный формат! Пример:\n<code>Война и мир - Лев Толстой</code>")
    
    title, author = message.text.split(' - ', 1)
    await Book.create(title=title.strip(), author=author.strip(), user=user)
    await message.answer(f"✅ Книга добавлена:\n\n<b>{title.strip()}</b>\nАвтор: {author.strip()}")
    await state.clear()

# @start_router.message(Form.waiting_for_book)
# async def process_book(message: Message, state: FSMContext):
#     if ' - ' not in message.text:
#         return await message.answer("❌ Неверный формат! Пример:\n<code>Война и мир - Лев Толстой</code>")
    
#     title, author = message.text.split(' - ', 1)
#     books.append({"title": title.strip(), "author": author.strip(), "votes": 0})
#     await message.answer(f"✅ Книга добавлена:\n\n<b>{title.strip()}</b>\nАвтор: {author.strip()}")
#     await state.clear()    

@start_router.message(Command('vote'))
@admin_required
async def cmd_vote(message: Message):
    books = await Book.select().where(Book.is_active == True).execute()
    
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
    
# @start_router.message(Command('vote'))
# async def cmd_vote(message: Message):
#     if not books:
#         return await message.answer("📚 Список книг пуст!")
    
#     builder = InlineKeyboardBuilder()
#     for index, book in enumerate(books):
#         builder.button(text=f"{book['title']} - {book['author']}", callback_data=f"vote_{index}")
    
#     builder.button(text="Проголосовать ✅", callback_data="submit_vote")
#     builder.adjust(1)
    
#     await message.answer(
#         "🗳 <b>Голосование началось!</b>\nВыберите книги:",
#         reply_markup=builder.as_markup()
#     )    


@start_router.callback_query(F.data.startswith("vote_"))
async def process_vote(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    user = await register_user(callback.from_user.id)
    
    # Проверяем, голосовал ли пользователь за эту книгу
    vote_exists = await Vote.select().where((Vote.user == user) & (Vote.book == book_id)).exists()
    if vote_exists:
        return await callback.answer("❌ Вы уже голосовали за эту книгу!")
    
    await Vote.create(user=user, book_id=book_id)
    await Book.update(votes=Book.votes + 1).where(Book.id == book_id).execute()
    await callback.answer("✅ Голос учтён!")
    
# @start_router.callback_query(F.data.startswith("vote_"))
# async def process_vote_selection(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     book_index = int(callback.data.split("_")[1])

#     # Проверяем, выбрал ли пользователь книгу
#     if user_id not in votes:
#         votes[user_id] = []

#     # Добавляем книгу в список голосов пользователя
#     if book_index not in votes[user_id]:
#         votes[user_id].append(book_index)
#         await callback.message.answer(f"✅ Книга <b>{books[book_index]['title']}</b> добавлена в голосование!")
#     else:
#         await callback.message.answer(f"❌ Вы уже голосовали за книгу <b>{books[book_index]['title']}</b>!")

#     # Обновляем клавиатуру
#     builder = InlineKeyboardBuilder()
#     for index, book in enumerate(books):
#         if index in votes[user_id]:
#             builder.button(text=f"✅ {book['title']} - {book['author']}", callback_data=f"vote_{index}")
#         else:
#             builder.button(text=f"{book['title']} - {book['author']}", callback_data=f"vote_{index}")
    
#     builder.button(text="Проголосовать ✅", callback_data="submit_vote")
#     builder.adjust(1)

#     await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

# @start_router.callback_query(F.data == "submit_vote")
# async def submit_vote(callback: CallbackQuery):
#     user_id = callback.from_user.id

#     if user_id not in votes or not votes[user_id]:
#         return await callback.message.answer("❌ Вы не выбрали ни одной книги для голосования!")

#     # Обработка голосов
#     for book_index in votes[user_id]:
#         books[book_index]['votes'] += 1

#     # Очищаем голоса пользователя
#     del votes[user_id]

#     await callback.message.edit_text("✅ Ваш голос учтен! 🗳 Голосование завершено. Спасибо за участие!")

    

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
    books = await Book.select().where(Book.is_active == True).execute()
    
    if not books:
        return await message.answer("📚 Список книг пуст!")
    
    random_book = random.choice(books)
    await message.answer(f"🎲 Случайная книга:\n\n<b>{random_book.title}</b>\nАвтор: {random_book.author}")

@start_router.message(Command('result'))
async def cmd_result(message: Message):
    books = await Book.select().order_by(Book.votes.desc()).execute()
    
    text = "📊 Результаты голосования:\n\n" + "\n".join(
        [f"{i+1}. {book.title} - {book.author}: {book.votes} гол." 
         for i, book in enumerate(books)]
    )
    await message.answer(text)
    
# @start_router.message(Command('random'))
# async def cmd_random(message: Message):
#     if not books:
#         return await message.answer("📚 Список книг пуст!")
    
#     random_book = random.choice(books)
#     await message.answer(f"🎲 Случайная книга:\n\n<b>{random_book['title']}</b>\nАвтор: {random_book['author']}")

# @start_router.message(Command('result'))
# async def cmd_result(message: Message):
#     if not books:
#         return await message.answer("📊 Нет данных о голосовании.")
    
#     text = "📊 Результаты голосования:\n\n" + "\n".join(
#         [f"{i+1}. {book['title']} - {book['author']}: {book['votes']} гол." 
#          for i, book in enumerate(books)]
#     )
    
#     # Определяем максимальное количество голосов
#     max_votes = max(book['votes'] for book in books)
    
#     # Находим все книги с максимальным количеством голосов
#     winners = [book for book in books if book['votes'] == max_votes]
    
#     if len(winners) > 1:
#         winners_text = "🏆 Победили книги:\n" + "\n".join(
#             [f"<b>{book['title']}</b> - <i>{book['author']}</i> с {book['votes']} голосами." for book in winners]
#         )
#     else:
#         winners_text = f"🏆 Победила книга: <b>{winners[0]['title']}</b> - <i>{winners[0]['author']}</i> с {winners[0]['votes']} голосами."

#     await message.answer(text + "\n\n" + winners_text)
    

# @start_router.message(Command('clear'))
# async def cmd_clear(message: Message):
#     global books, votes
#     books = []
#     votes = {}
#     await message.answer("✅ Данные о книгах очищены. Теперь вы можете добавлять новые книги.")    
