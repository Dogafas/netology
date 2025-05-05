# app\crud\__init__.py
from .user import get_user_by_id, get_user_by_email, create_user
from .advertisement import (
    create_advertisement,
    get_advertisement_by_id,
    get_advertisements,
    update_advertisement,
    delete_advertisement,
)

__all__ = [
    # User CRUD
    "get_user_by_id",
    "get_user_by_email",
    "create_user",
    # Advertisement CRUD
    "create_advertisement",
    "get_advertisement_by_id",
    "get_advertisements",
    "update_advertisement",
    "delete_advertisement",
]
