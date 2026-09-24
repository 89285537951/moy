from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, BigInteger, Text


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class FurnitureType(Base):
    __tablename__ = "furniture_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class Furniture(Base):
    __tablename__ = "furniture"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    type_id: Mapped[int | None] = mapped_column(ForeignKey("furniture_types.id"), nullable=True)

    photos = relationship("FurniturePhoto", back_populates="furniture", cascade="all, delete-orphan")
    category = relationship("Category")
    country = relationship("Country")
    furniture_type = relationship("FurnitureType")


class FurniturePhoto(Base):
    __tablename__ = "furniture_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    furniture_id: Mapped[int] = mapped_column(ForeignKey("furniture.id", ondelete="CASCADE"))
    file_id: Mapped[str] = mapped_column(String)

    furniture = relationship("Furniture", back_populates="photos")