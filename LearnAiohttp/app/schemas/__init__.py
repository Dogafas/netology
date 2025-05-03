# app\schemas\__init__.py
from .user import UserBase, UserCreate, UserLogin, UserResponse
from .advertisement import (
    AdvertisementBase,
    AdvertisementCreate,
    AdvertisementUpdate,
    AdvertisementResponse,
)
from .token import Token, TokenData

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    # Advertisement schemas
    "AdvertisementBase",
    "AdvertisementCreate",
    "AdvertisementUpdate",
    "AdvertisementResponse",
    # Token schemas
    "Token",
    "TokenData",
]
