import asyncio
import logging

from aiogram import Dispatcher

from settings.config import bot
from database.engine import init_db, ensure_admins
from handlers import router as main_router
from middlewares.db import DbSessionMiddleware


async def main():
    await init_db()
    await ensure_admins()

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(main_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот успешно запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")