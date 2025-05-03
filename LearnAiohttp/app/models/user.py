# app\models\user.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """
    Модель пользователя.

    Представляет таблицу 'users' в базе данных.
    """

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    password_hash: str = Column(String, nullable=False)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связь с объявлениями: один пользователь может иметь много объявлений
    advertisements = relationship(
        "Advertisement",  # Строка с именем связанного класса
        back_populates="owner",  # Имя атрибута в связанной модели для двунаправленной связи
        cascade="all, delete-orphan",  # При удалении пользователя удаляются и его объявления
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
