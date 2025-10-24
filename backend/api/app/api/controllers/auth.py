"""
Auth Controller (API endpoints)

Endpoints de autenticación y gestión de usuarios.
Incluye operaciones CRUD completas.
"""

import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import storage
from app.models.sender import Sender

bp = Blueprint("auth", __name__)

# Directorio base de documentación
CONTROLLERS_DIR = os.path.dirname(__file__)
DOC_AUTH_DIR = os.path.abspath(os.path.join(CONTROLLERS_DIR, "documentation", "auth"))

# ------------------------
# POST /api/auth/register
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "post_register.yaml"))
@bp.route("/register", methods=["POST"])
def register():
    """Registrar un nuevo usuario"""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not all([email, password, first_name, last_name]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    if any(s.email == email for s in storage.all(Sender).values()):
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 409

    user = Sender(
        id=str(uuid.uuid4()),
        email=email,
        first_name=first_name,
        last_name=last_name,
        type="user"
    )
    user.set_password(password)
    storage.new(user)

    return jsonify({
        "status": "success",
        "message": "Usuario registrado exitosamente.",
        "user": user.to_dict()
    }), 201


# ------------------------
# POST /api/auth/login
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "post_login.yaml"))
@bp.route("/login", methods=["POST"])
def login():
    """Iniciar sesión"""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Email y contraseña son obligatorios"}), 400

    users = [s for s in storage.all(Sender).values() if s.email == email]
    if not users:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    user = users[0]
    if not user.check_password(password):
        return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 401

    # (Simulación de token)
    token = str(uuid.uuid4())

    return jsonify({
        "status": "success",
        "message": "Inicio de sesión exitoso",
        "token": token,
        "user": user.to_dict()
    }), 200


# ------------------------
# GET /api/auth/me
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "get_me.yaml"))
@bp.route("/me", methods=["GET"])
def get_me():
    """Devuelve un usuario simulado autenticado (para pruebas)"""
    # En un entorno real se obtendría desde el token JWT
    mock_user = next(iter(storage.all(Sender).values()), None)
    if not mock_user:
        return jsonify({"status": "error", "message": "No hay usuarios registrados"}), 404

    return jsonify({"status": "success", "user": mock_user.to_dict()}), 200


# ------------------------
# GET /api/auth
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "get_all.yaml"))
@bp.route("", methods=["GET"])
def list_users():
    """Listar todos los usuarios"""
    users = [u.to_dict() for u in storage.all(Sender).values()]
    return jsonify({"status": "success", "data": users}), 200


# ------------------------
# GET /api/auth/<user_id>
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "get_user.yaml"))
@bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """Obtener usuario por ID"""
    user = storage.get(Sender, user_id)
    if not user:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    return jsonify({"status": "success", "data": user.to_dict()}), 200


# ------------------------
# PUT /api/auth/<user_id>
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "put_user.yaml"))
@bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    """Actualizar usuario"""
    user = storage.get(Sender, user_id)
    if not user:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    data = request.get_json() or {}
    for key in ["first_name", "last_name", "email"]:
        if key in data:
            setattr(user, key, data[key])

    if "password" in data:
        user.set_password(data["password"])

    storage.save()

    return jsonify({"status": "success", "message": "Usuario actualizado", "data": user.to_dict()}), 200


# ------------------------
# DELETE /api/auth/<user_id>
# ------------------------
@swag_from(os.path.join(DOC_AUTH_DIR, "delete_user.yaml"))
@bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Eliminar usuario"""
    user = storage.get(Sender, user_id)
    if not user:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    storage.delete(user)
    storage.save()

    return jsonify({"status": "success", "message": "Usuario eliminado"}), 200
