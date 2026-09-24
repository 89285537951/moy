from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from database.engine import AsyncSessionLocal
from database.models import Category, Furniture, FurniturePhoto, User


async def set_user(telegram_id: int, username: str | None, first_name: str | None):
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            session.add(User(telegram_id=telegram_id, username=username, first_name=first_name))
            await session.commit()


async def is_admin(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        return bool(user and user.is_admin)


async def get_categories():
    async with AsyncSessionLocal() as session:
        result = await session.scalars(select(Category).order_by(Category.id))
        return result.all()


async def get_category(category_id: int):
    async with AsyncSessionLocal() as session:
        return await session.get(Category, category_id)


async def add_category(name: str, description: str | None = None) -> bool:
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Category).where(Category.name == name))
        if existing:
            return False
        session.add(Category(name=name, description=description))
        await session.commit()
        return True


async def add_furniture(
    description: str,
    category_name: str,
    country_origin: str,
    photos: list[str],
    furniture_type: str | None = None,
):
    async with AsyncSessionLocal() as session:
        item = Furniture(
            category_name=category_name,
            furniture_type=furniture_type,
            country_origin=country_origin,
            description=description,
        )
        session.add(item)
        await session.flush()

        session.add_all([
            FurniturePhoto(furniture_id=item.id, file_path=file_id)
            for file_id in photos
        ])
        await session.commit()
        return item.id


async def get_furniture_by_category(category_name: str, country_origin: str | None = None):
    async with AsyncSessionLocal() as session:
        query = (
            select(Furniture)
            .options(selectinload(Furniture.photos))
            .where(Furniture.category_name == category_name)
            .order_by(Furniture.id)
        )
        if country_origin:
            query = query.where(Furniture.country_origin == country_origin)
        result = await session.scalars(query)
        return result.all()


async def get_all_furniture():
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(Furniture).options(selectinload(Furniture.photos)).order_by(Furniture.id)
        )
        return result.all()


async def delete_furniture(furniture_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        furniture = await session.get(Furniture, furniture_id)
        if furniture is None:
            return False
        await session.execute(delete(FurniturePhoto).where(FurniturePhoto.furniture_id == furniture_id))
        await session.delete(furniture)
        await session.commit()
        return True
