from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from database.engine import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(64), nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)


class Furniture(Base):
    __tablename__ = "furniture"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    furniture_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    country_origin = Column(String(100), nullable=False)

    photos = relationship(
        "FurniturePhoto",
        back_populates="furniture",
        cascade="all, delete-orphan",
    )


class FurniturePhoto(Base):
    __tablename__ = "furniture_photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    furniture_id = Column(
        Integer,
        ForeignKey("furniture.id", ondelete="CASCADE"),
        nullable=False,
    )

    file_path = Column(Text, nullable=False)

    furniture = relationship("Furniture", back_populates="photos")
