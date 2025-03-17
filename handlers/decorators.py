from functools import wraps
from aiogram.types import Message
from create_bot import admins


def admin_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in admins:
            await message.answer("🚫 Эта команда доступна только администраторам!")
            return
        return await func(message, *args, **kwargs)
    return wrapper
