import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.models import Base, Category, Furniture, FurniturePhoto, Country, FurnitureType

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"

DB_URL = os.getenv("DB_URL", f"sqlite+aiosqlite:///{DB_PATH}")

async_engine = create_async_engine(DB_URL, echo=False)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

AsyncSessionLocal = async_session_maker

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


migrate_database = init_db


async def async_main():
    await init_db()


async def ensure_admins():
    pass