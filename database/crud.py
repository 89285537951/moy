from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from .models import Category, Furniture, FurniturePhoto, User, Country, FurnitureType


class CrudUser:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def set_user(self, telegram_id: int, username: str = None, first_name: str = None):
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            self.session.add(user)
            await self.session.commit()
        return user


class CrudCategory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_category(self, name: str, description: str = None) -> bool:
        new_category = Category(name=name, description=description)
        self.session.add(new_category)
        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def get_all_categories(self):
        result = await self.session.execute(select(Category))
        return result.scalars().all()

    async def get_by_id(self, category_id: int):
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()


class CrudCountry:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_country(self, name: str) -> Country:
        result = await self.session.execute(select(Country).where(Country.name == name))
        country = result.scalar_one_or_none()
        if not country:
            country = Country(name=name)
            self.session.add(country)
            await self.session.commit()
            await self.session.refresh(country)
        return country


class CrudFurnitureType:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_type(self, name: str) -> FurnitureType:
        result = await self.session.execute(select(FurnitureType).where(FurnitureType.name == name))
        ftype = result.scalar_one_or_none()
        if not ftype:
            ftype = FurnitureType(name=name)
            self.session.add(ftype)
            await self.session.commit()
            await self.session.refresh(ftype)
        return ftype


class CrudFurniture:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_furniture(self, title: str, description: str, category_id: int,
                            country_id: int, type_id: int | None = None) -> Furniture:
        furniture = Furniture(
            title=title,
            description=description,
            category_id=category_id,
            country_id=country_id,
            type_id=type_id,
        )
        self.session.add(furniture)
        await self.session.commit()
        await self.session.refresh(furniture)
        return furniture

    async def add_furniture_photo(self, furniture_id: int, file_id: str):
        photo = FurniturePhoto(furniture_id=furniture_id, file_id=file_id)
        self.session.add(photo)
        await self.session.commit()

    async def get_furniture_photos(self, furniture_id: int):
        result = await self.session.execute(
            select(FurniturePhoto).where(FurniturePhoto.furniture_id == furniture_id)
        )
        return result.scalars().all()

    async def get_all_furniture(self):
        result = await self.session.execute(
            select(Furniture).options(selectinload(Furniture.photos))
        )
        return result.scalars().all()

    async def get_by_category_and_country(self, category_id: int, country_name: str):
        result = await self.session.execute(
            select(Furniture)
            .join(Country, Furniture.country_id == Country.id)
            .options(
                selectinload(Furniture.photos),
                selectinload(Furniture.country),
                selectinload(Furniture.furniture_type),
            )
            .where(Furniture.category_id == category_id, Country.name == country_name)
        )
        return result.scalars().all()

    async def delete_furniture(self, furniture_id: int) -> bool:
        result = await self.session.execute(delete(Furniture).where(Furniture.id == furniture_id))
        await self.session.commit()
        return result.rowcount > 0