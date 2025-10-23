#!/usr/bin/env python3
"""
Auth Controller (API endpoints)

Handles user (Sender) registration, login, and authentication token management.
"""

import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, EmailStr, constr, ValidationError
from app.models import storage
from app.models.sender import Sender, SenderType

bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------
class RegisterSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    first_name: str
    last_name: str
    type: str = "user"  # 'user' or 'admin'


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------
@bp.route("/register", methods=["POST"])
def register():
    """Register a new user or admin."""
    try:
        payload = RegisterSchema(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"status": "error", "error": e.errors()}), 400

    # Check if email exists
    existing = [s for s in storage.all(Sender).values() if s.email == payload.email]
    if existing:
        return jsonify({
            "status": "error",
            "error": {"code": "EMAIL_EXISTS", "message": "El correo ya está registrado."}
        }), 409

    # Create user
    sender = Sender(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        type=SenderType.USER if payload.type == "user" else SenderType.SYSTEM,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    sender.set_password(payload.password)

    try:
        storage.new(sender)
    except Exception as e:
        current_app.logger.exception("Error saving sender")
        return jsonify({"status": "error", "message": str(e)}), 500

    token = create_access_token(
        identity={"email": sender.email, "role": sender.type.value},
        expires_delta=timedelta(hours=8)
    )

    return jsonify({
        "status": "success",
        "data": {
            "token": token,
            "email": sender.email,
            "role": sender.type.value,
            "first_name": sender.first_name,
            "last_name": sender.last_name
        }
    }), 201


# ---------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------
@bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        payload = LoginSchema(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"status": "error", "error": e.errors()}), 400

    # Find user
    sender = None
    for s in storage.all(Sender).values():
        if s.email == payload.email:
            sender = s
            break

    if not sender or not sender.check_password(payload.password):
        return jsonify({
            "status": "error",
            "error": {"code": "INVALID_CREDENTIALS", "message": "Correo o contraseña incorrectos."}
        }), 401

    token = create_access_token(
        identity={"email": sender.email, "role": sender.type.value},
        expires_delta=timedelta(hours=8)
    )

    return jsonify({
        "status": "success",
        "data": {
            "token": token,
            "email": sender.email,
            "role": sender.type.value,
            "first_name": sender.first_name,
            "last_name": sender.last_name
        }
    }), 200


# ---------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------
@bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Get info of currently authenticated user."""
    identity = get_jwt_identity()
    return jsonify({"status": "success", "data": identity}), 200


# ---------------
