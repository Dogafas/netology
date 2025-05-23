# app\models.py

from sqlalchemy import (
    Integer,
    String,
    Numeric,
    DateTime,
    func,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import List
from .database import Base


# Enum для групп пользователей
class UserGroup(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )  # Email обязателен и уникален
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    group: Mapped[UserGroup] = mapped_column(
        SQLAlchemyEnum(UserGroup, name="user_group_enum", create_type=False),
        default=UserGroup.USER,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Связь с объявлениями: один пользователь может иметь много объявлений
    advertisements: Mapped[List["Advertisement"]] = relationship(
        "Advertisement",
        back_populates="owner",
        cascade="all, delete-orphan",  # Если пользователя удаляют, его объявления тоже удаляются
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', group='{self.group.value}')>"


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Внешний ключ для связи с пользователем-владельцем
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    # Связь с пользователем: объявление принадлежит одному пользователю
    owner: Mapped["User"] = relationship("User", back_populates="advertisements")

    def __repr__(self):
        return f"<Advertisement(id={self.id}, title='{self.title}', owner_id={self.owner_id}, author='{self.author}')>"
