import os

from dotenv import load_dotenv
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def migrate_database():
    async with async_engine.begin() as conn:
        categories = await conn.execute(text("PRAGMA table_info(categories)"))
        category_columns = [row[1] for row in categories.fetchall()]
        if "description" not in category_columns:
            await conn.execute(text("ALTER TABLE categories ADD COLUMN description TEXT"))

        furniture = await conn.execute(text("PRAGMA table_info(furniture)"))
        furniture_columns = [row[1] for row in furniture.fetchall()]
        if "furniture_type" not in furniture_columns:
            await conn.execute(text("ALTER TABLE furniture ADD COLUMN furniture_type VARCHAR(100)"))


        await conn.execute(text(
            "UPDATE furniture SET furniture_type = country_origin, country_origin = 'Россия' "
            "WHERE category_name = 'Кухонная мебель' "
            "AND country_origin IN ('Прямая кухня', 'Угловая кухня') "
            "AND (furniture_type IS NULL OR furniture_type = '')"
        ))


async def ensure_admins():
    raw_ids = os.getenv("ADMIN_IDS", "")
    admin_ids = {int(value.strip()) for value in raw_ids.split(",") if value.strip().isdigit()}
    if not admin_ids:
        return

    from database.models import User

    async with AsyncSessionLocal() as session:
        for telegram_id in admin_ids:
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
            if user:
                user.is_admin = True
            else:
                session.add(User(telegram_id=telegram_id, is_admin=True))
        await session.commit()


async def async_main():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await migrate_database()
