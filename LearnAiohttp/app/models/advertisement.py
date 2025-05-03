# app\models\advertisement.py
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Advertisement(Base):
    """
    Модель объявления.

    Представляет таблицу 'advertisements' в базе данных.
    """

    __tablename__ = "advertisements"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(100), nullable=False)
    description: str = Column(Text, nullable=True)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    owner_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )  # Внешний ключ к таблице пользователей

    # Связь с пользователем: каждое объявление принадлежит одному пользователю
    owner = relationship("User", back_populates="advertisements")

    def __repr__(self):
        return (
            f"<Advertisement(id={self.id}, title='{self.title}', "
            f"owner_id={self.owner_id})>"
        )
