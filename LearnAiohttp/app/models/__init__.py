# app\models\__init__.py
from .base import Base
from .user import User
from .advertisement import Advertisement


__all__ = [
    "Base",
    "User",
    "Advertisement",
]
