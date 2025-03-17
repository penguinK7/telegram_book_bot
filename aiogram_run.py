import asyncio
import logging
from create_bot import dp, bot, scheduler
from db_handler.db_class import create_tables
from handlers.start import start_router


async def main():
    try:
        # Создаем таблицы в базе данных
        create_tables()
        logging.info("Таблицы успешно созданы.")

        # Подключаем роутер
        dp.include_router(start_router)
        logging.info("Роутер успешно подключен.")

        # Запускаем планировщик
        scheduler.start()
        logging.info("Планировщик успешно запущен.")

        # Запускаем бота
        logging.info("Запускаем бота")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        logging.info("Выключаем книжного бота")
        await bot.session.close()
        scheduler.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
