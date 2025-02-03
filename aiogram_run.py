import asyncio
from create_bot import dp, bot, scheduler
from db_handler.db_class import create_tables
from handlers.start import start_router
# fdgdfj
async def main():
    # Создаем таблицы в базе данных
    create_tables()
    
    # Подключаем роутер
    dp.include_router(start_router)
    
    # Запускаем планировщик
    scheduler.start()
    
    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())