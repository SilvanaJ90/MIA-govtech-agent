#!/usr/bin/python3
"""
Test module for Session model.

This module contains pytest tests for the `Session` SQLAlchemy model,
focusing on session creation and attribute validation.

Tests include:
- Creating a session and verifying its user association
- Ensuring required attributes exist
"""

import pytest
from app.models.session import Session


def test_session_creation(session, sender):
    """
    Test creating a new session for a sender.

    Ensures that:
    - The session's user_id matches the sender's ID
    - The session has a 'session_id' attribute
    """
    assert session.user_id == sender.id
    assert hasattr(session, "session_id")
