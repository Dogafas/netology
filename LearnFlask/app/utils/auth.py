# app/utils/auth.py
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from .. import db


def get_current_user():
    user_id = get_jwt_identity()
    return db.session.get(User, user_id)
