from typing import List

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.engine import AsyncSessionLocal
from database.models import Category, Furniture, FurniturePhoto


class CrudCategory:
    async def get_all_categories(self) -> List[Category]:
        async with AsyncSessionLocal() as session:
            result = await session.scalars(select(Category).order_by(Category.id))
            return result.all()

    async def check_category_by_name(self, name: str) -> bool:
        async with AsyncSessionLocal() as session:
            return await session.scalar(select(Category).where(Category.name == name)) is not None

    async def create_category(self, name: str, description: str | None = None) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                if await session.scalar(select(Category).where(Category.name == name)):
                    return False
                session.add(Category(name=name, description=description))
                await session.commit()
                return True
            except (IntegrityError, SQLAlchemyError):
                await session.rollback()
                return False


class CrudFurniture:
    async def create_furniture(
        self,
        category_name: str,
        description: str,
        param: str,
        photos: List[str],
        furniture_type: str | None = None,
    ) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                category = await session.scalar(select(Category).where(Category.name == category_name))
                if not category:
                    return False

                item = Furniture(
                    category_name=category.name,
                    furniture_type=furniture_type,
                    description=description,
                    country_origin=param,
                )
                session.add(item)
                await session.flush()

                for file_id in photos:
                    session.add(FurniturePhoto(furniture_id=item.id, file_path=file_id))

                await session.commit()
                return True
            except (IntegrityError, SQLAlchemyError):
                await session.rollback()
                return False
