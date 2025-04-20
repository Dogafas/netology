# app/routes/adverts.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.advert import Advert
from app.utils.auth import get_current_user
from app import db

adverts_bp = Blueprint("adverts", __name__)


@adverts_bp.route("/", methods=["POST"])
@jwt_required()
def create_advert():
    user = get_current_user()
    data = request.get_json()

    if not data.get("title") or not data.get("description"):
        return jsonify({"message": "Title and description are required"}), 400

    advert = Advert(
        title=data["title"], description=data["description"], owner_id=user.id
    )
    db.session.add(advert)
    db.session.commit()

    return jsonify(advert.to_dict()), 201


@adverts_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_advert(id):
    user = get_current_user()
    advert = Advert.query.get_or_404(id)

    if advert.owner_id != user.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    advert.title = data.get("title", advert.title)
    advert.description = data.get("description", advert.description)
    db.session.commit()

    return jsonify(advert.to_dict()), 200


@adverts_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_advert(id):
    user = get_current_user()
    advert = Advert.query.get_or_404(id)

    if advert.owner_id != user.id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(advert)
    db.session.commit()

    return jsonify({"message": "Advert deleted"}), 200


@adverts_bp.route("/", methods=["GET"])
def get_adverts():
    adverts = Advert.query.all()
    return jsonify([advert.to_dict() for advert in adverts]), 200
