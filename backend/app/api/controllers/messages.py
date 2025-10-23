"""
Messages Controller (API endpoints)

This module implements the HTTP endpoints
for sending and retrieving chat messages.
It uses Pydantic for input validation and
Flasgger for operation-level Swagger YAML.
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, Response
from pydantic import ValidationError
from flasgger import swag_from

from app.api.schemas import MessageIn
from app.api.services.message_service import MessageService
from app.models import storage
from app.models.session import Session
from app.models.sender import SenderType

bp = Blueprint("messages", __name__)

# Directory helpers for Swagger YAML files
CONTROLLERS_DIR = os.path.dirname(__file__)
DOC_MESSAGES_DIR = os.path.abspath(os.path.join(
    CONTROLLERS_DIR, "documentation", "messages"))


# ---------------------
# Helper: safe_swag_from
# ---------------------
def safe_swag_from(path):
    """
    Safe wrapper around flasgger.swag_from that becomes a no-op decorator
    if the YAML file does not exist. Prevents import-time failures or empty
    operations when YAML is missing or inaccessible in some environments.
    """
    if path and os.path.exists(path):
        return swag_from(path)

    # no-op decorator
    def _decorator(f):
        return f
    return _decorator


@safe_swag_from(os.path.join(DOC_MESSAGES_DIR, "post_messages.yaml"))
@bp.route("", methods=["POST"])
def post_message():
    """
    POST /api/messages
    Accepts payload validated by MessageIn (Pydantic).
    """
    try:
        payload = request.get_json() or {}
    except Exception:
        return jsonify(
            {"status": "error", "error": {
                "code": "INVALID_REQUEST", "message": "Invalid JSON"}}), 400

    # Normalize legacy 'sender' field
    if "sender" in payload and "sender_id" not in payload and "sender_type" not in payload:
        if payload["sender"] in ("user", "system", "bot"):
            payload["sender_type"] = payload["sender"]
        else:
            payload["sender_id"] = payload["sender"]
        payload.pop("sender", None)

    # Validate payload with Pydantic
    try:
        validated = MessageIn(**payload)
    except ValidationError as ve:
        return Response(ve.json(), status=400, mimetype="application/json")
    except Exception as e:
        current_app.logger.exception("Invalid request")
        return jsonify(
            {"status": "error", "error": {
                "code": "INVALID_REQUEST", "message": str(e)}}), 400

    # ------------------ DEBUG INFO (temporal) ------------------
    try:
        # Raw payload received
        current_app.logger.debug("POST /api/messages payload: %s", payload)
        # Pydantic-normalized fields
        current_app.logger.debug("validated.sender_type: %s", getattr(validated, "sender_type", None))
        current_app.logger.debug("validated.session_id: %s", getattr(validated, "session_id", None))
        # What sessions storage currently has (in THIS process)
        sess_ids = [getattr(s, "session_id", None) for s in storage.all(Session).values()]
        current_app.logger.debug("Sessions in storage at POST time: %s", sess_ids)
    except Exception:
        current_app.logger.exception("Debug logging failed")
    # -----------------------------------------------------------


    if validated.sender_type:
        validated.sender_type = validated.sender_type.lower()

    create_payload = {
        "sender_id": validated.sender_id,
        "sender_type": validated.sender_type,
        "content": validated.content,
        "session_id": validated.session_id
    }

    try:
        msg, session_id = MessageService.create_message(create_payload)
    except ValueError as ve:
        return jsonify(
            {
                "status": "error",
                "error": {"code": "NOT_FOUND", "message": str(ve)}}), 404
    except PermissionError as pe:
        return jsonify(
            {
                "status": "error",
                "error": {"code": "FORBIDDEN", "message": str(pe)}}), 403
    except Exception:
        current_app.logger.exception("Error creating message")
        return jsonify(
            {"status": "error", "error": {
                "code": "SERVER_ERROR", "message": "Internal error"}}), 500

    out = {
        "status": "success",
        "data": {
            "message_id": getattr(msg, "message_id", None),
            "session_id": session_id,
            "content": getattr(msg, "content", None),
            "timestamp": (getattr(msg, "timestamp", None).isoformat() + "Z"),
            "sender": validated.sender_id if validated.sender_id else (
                validated.sender_type if validated.sender_type else None),
            "metadata": msg.get_metadata() if hasattr(
                msg, "get_metadata") else {}
        }
    }
    return jsonify(out), 201


@safe_swag_from(os.path.join(DOC_MESSAGES_DIR, "get_messages_session_id.yaml"))
@bp.route("/<session_id>", methods=["GET"], strict_slashes=False)
def get_messages(session_id):
    """
    GET /api/messages/<session_id>
    """
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except Exception:
        return jsonify(
            {"status": "error", "error": {
                "code": "INVALID_REQUEST",
                "message": "limit and offset must be integers"}}), 400

    sender_filter = request.args.get("sender", None)

    # verify session exists (Session.session_id is the public identifier)
    sess = None
    for s in storage.all(Session).values():
        if getattr(s, "session_id", None) == session_id:
            sess = s
            break
    if not sess:
        return jsonify({
            "status": "error",
            "error": {"code": "NOT_FOUND", "message": "Session not found"}
            }), 404

    try:
        msgs = MessageService.list_messages(
            session_id, limit=limit, offset=offset, sender=sender_filter)
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "error": {"code": "NOT_FOUND", "message": str(ve)}}), 404
    except Exception:
        current_app.logger.exception("Error listing messages")
        return jsonify({
            "status": "error",
            "error": {"code": "SERVER_ERROR", "message": "Internal error"}
            }), 500

    out = []
    for m in msgs:
        out.append({
            "message_id": getattr(m, "message_id", None),
            "session_id": getattr(m, "session_id", None),
            "content": getattr(m, "content", None),
            "timestamp": getattr(m, "timestamp", None).isoformat() +
            "Z" if getattr(m, "timestamp", None) else None,
            "sender_id": getattr(m, "sender_id", None),
            "metadata": m.get_metadata() if hasattr(m, "get_metadata") else {}
        })

    return jsonify({"status": "success", "data": out}), 200
