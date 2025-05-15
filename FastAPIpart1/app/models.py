from sqlalchemy import Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from .database import Base


class Advertisement(Base):
    """
    Модель SQLAlchemy для представления объявления в базе данных.
    """

    __tablename__ = "advertisements"  # Явное указание имени таблицы

    # Первичный ключ, автоинкремент
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Заголовок объявления, обязательное поле
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # Ограничим длину заголовка

    # Описание объявления, необязательное поле
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # Ограничим длину описания

    # Цена, обязательное поле. Numeric(10, 2) - до 10 знаков всего, 2 после запятой
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, index=True)

    # Автор объявления, обязательное поле
    author: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # Ограничим длину имени автора

    # Дата и время создания записи (с временной зоной)
    # Устанавливается автоматически при создании записи на стороне БД
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Значение по умолчанию - текущее время БД
        nullable=False,
        index=True,  # Индекс для возможной сортировки по дате создания
    )

    # Дата и время последнего обновления записи (с временной зоной)
    # Устанавливается при создании и обновляется автоматически при изменении записи
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Значение при создании
        onupdate=func.now(),  # Значение при обновлении
        nullable=False,
    )

    # Дополнительно можно определить __repr__ для удобного вывода объекта
    def __repr__(self):
        return f"<Advertisement(id={self.id}, title='{self.title}', price={self.price}, author='{self.author}')>"
