#!/usr/bin/python3
"""
Test module for Sender model.

This module contains pytest tests for the `Sender` SQLAlchemy model,
focusing on password hashing, creation, and updates.

Tests include:
- Sender creation with a valid email and password
- Updating the sender's password and verifying it
"""

import pytest
from app.models.sender import Sender
from app.models.storage import new, delete


def test_sender_creation(sender):
    """
    Test creating a new sender.

    Ensures that the sender's email is correctly set and that the password
    can be verified using `check_password`.
    """
    assert sender.email.startswith("test_")
    assert sender.check_password("1234")


def test_sender_password_update(sender):
    """
    Test updating a sender's password.

    Sets a new password and verifies that `check_password` returns True
    for the updated password.
    """
    sender.set_password("newpass")
    assert sender.check_password("newpass")
