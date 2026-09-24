import asyncio
import logging

from aiogram import Dispatcher

from settings.config import bot
from database.engine import async_engine, Base, migrate_database, ensure_admins
from handlers import router as main_router


async def main():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await migrate_database()
    await ensure_admins()

    dp = Dispatcher()
    dp.include_router(main_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот успешно запущен и ожидает сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
