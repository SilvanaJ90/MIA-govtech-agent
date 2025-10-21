#!/usr/bin/python3
"""
Test module for /api/messages endpoints and message schemas.

This module contains pytest tests for the message-related API endpoints
in the chat application, including both POST and GET requests. It also
tests the Pydantic schemas `MessageIn` and `MessageOut` for validation
and serialization.

Tests include:
- Posting messages with valid, invalid, or forbidden content
- Retrieving messages for valid and invalid sessions
- Handling service exceptions and payload errors
- Schema validation and serialization checks
"""

import pytest
from app.models.message import Message
from app.models.banned_word import BannedWord
from app.api.schemas import MessageIn, MessageOut
from unittest.mock import patch
from datetime import datetime, timezone

# -------------------------
# POST /api/messages Tests
# -------------------------


def test_post_message_minimal(client, sender):
    """
    Test posting a minimal valid message.

    Checks that a message with content and sender_id is accepted,
    returns 201, and the response JSON contains the correct data.
    """
    payload = {"content": "Hola test", "sender_id": sender.id}
    rv = client.post("/api/messages", json=payload)
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["status"] == "success"
    assert data["data"]["content"] == "Hola test"
    assert data["data"]["sender"] == sender.id


def test_post_message_sender_not_found(client):
    """
    Test posting a message with a non-existent sender.

    Expects a 404 NOT_FOUND response.
    """
    payload = {"content": "Hola test", "sender_id": "non-existent-id"}
    rv = client.post("/api/messages", json=payload)
    assert rv.status_code == 404
    data = rv.get_json()
    assert data["error"]["code"] == "NOT_FOUND"


def test_post_message_banned_word(client, sender):
    """
    Test posting a message that contains a banned word.

    Expects a 403 FORBIDDEN response.
    """
    bw = BannedWord(word="prohibido")
    from app.models.storage import new, delete
    new(bw)
    try:
        payload = {"content": "Esto tiene prohibido", "sender_id": sender.id}
        rv = client.post("/api/messages", json=payload)
        assert rv.status_code == 403
        data = rv.get_json()
        assert data["error"]["code"] == "FORBIDDEN"
    finally:
        delete(bw)


def test_post_message_legacy_sender_user(client, sender):
    """
    Test posting a message using the legacy
    'sender' field instead of 'sender_id'.
    Ensures backward compatibility with older clients.
    """
    payload = {"content": "Hola legacy sender", "sender": sender.id}
    rv = client.post("/api/messages", json=payload)
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["status"] == "success"


def test_post_message_invalid_json(client):
    """
    Test posting a message with invalid JSON.

    Expects a 400 INVALID_REQUEST response.
    """
    rv = client.post(
        "/api/messages", data="not a json", content_type="application/json")
    assert rv.status_code == 400
    assert rv.get_json()["error"]["code"] == "INVALID_REQUEST"


def test_post_message_invalid_payload(client, sender):
    """
    Test posting a message with an invalid
    payload type (e.g., content is integer).

    Expects a 400 response with error message including 'content'.
    """
    payload = {"content": 12345, "sender_id": sender.id}
    rv = client.post("/api/messages", json=payload)
    assert rv.status_code == 400
    assert "content" in rv.data.decode()


def test_post_message_service_exception(client, sender):
    """
    Test that an exception in the service layer returns a 500 SERVER_ERROR.
    """
    payload = {"content": "trigger exception", "sender_id": sender.id}
    with patch("app.api.services.message_service.MessageService.create_message") as mock_create:
        mock_create.side_effect = Exception("Server error")
        rv = client.post("/api/messages", json=payload)
        assert rv.status_code == 500
        assert rv.get_json()["error"]["code"] == "SERVER_ERROR"


# -------------------------
# GET /api/messages/<session_id> Tests
# -------------------------

def test_get_messages(client, sender, session):
    """
    Test retrieving messages for a valid session.

    Checks that messages are returned correctly in JSON format.
    """
    from app.models.storage import new, delete
    msg = Message(
        content="Hola GET", sender_id=sender.id, session_id=session.session_id)
    new(msg)
    try:
        rv = client.get(f"/api/messages/{session.session_id}")
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1
        assert data["data"][0]["content"] == "Hola GET"
    finally:
        delete(msg)


def test_get_messages_invalid_session(client):
    """
    Test retrieving messages for a non-existent session.

    Expects a 404 NOT_FOUND response.
    """
    rv = client.get("/api/messages/invalid-session-id")
    assert rv.status_code == 404
    assert rv.get_json()["error"]["code"] == "NOT_FOUND"


def test_get_messages_invalid_limit_offset(client, session):
    """
    Test GET messages with invalid query parameters (limit, offset).

    Expects a 400 INVALID_REQUEST response.
    """
    rv = client.get(f"/api/messages/{session.session_id}?limit=abc&offset=xyz")
    assert rv.status_code == 400
    assert rv.get_json()["error"]["code"] == "INVALID_REQUEST"


def test_get_messages_service_value_error(client, session):
    """
    Test that a ValueError in service layer returns 404 NOT_FOUND.
    """
    with patch("app.api.services.message_service.MessageService.list_messages") as mock_list:
        mock_list.side_effect = ValueError("Session not found")
        rv = client.get(f"/api/messages/{session.session_id}")
        assert rv.status_code == 404
        assert rv.get_json()["error"]["code"] == "NOT_FOUND"


def test_get_messages_service_exception(client, session):
    """
    Test that a general exception in service layer returns 500 SERVER_ERROR.
    """
    with patch("app.api.services.message_service.MessageService.list_messages") as mock_list:
        mock_list.side_effect = Exception("Server error")
        rv = client.get(f"/api/messages/{session.session_id}")
        assert rv.status_code == 500
        assert rv.get_json()["error"]["code"] == "SERVER_ERROR"


# -------------------------
# Additional schema and validation tests
# -------------------------

def test_message_in_valid_and_invalid():
    """
    Test validation rules of MessageIn schema.

    Checks valid input, invalid sender_type, and empty content.
    """
    # Valid input
    valid = {"content": "test", "sender_type": "user"}
    mi = MessageIn(**valid)
    assert mi.content == "test"

    # Invalid sender_type
    invalid = {"content": "test", "sender_type": "invalid"}
    with pytest.raises(ValueError):
        MessageIn(**invalid)

    # Empty content
    empty = {"content": "   "}
    with pytest.raises(ValueError):
        MessageIn(**empty)


def test_message_out_serialization():
    """
    Test serialization of MessageOut schema.

    Ensures the model dumps correctly to a dictionary with expected fields.
    """
    mo = MessageOut(
        message_id="123",
        session_id="sess1",
        content="hello",
        timestamp=datetime.now(timezone.utc),
        sender="user",
        metadata={}
    )
    data = mo.model_dump()
    assert data["message_id"] == "123"
    assert data["sender"] == "user"
