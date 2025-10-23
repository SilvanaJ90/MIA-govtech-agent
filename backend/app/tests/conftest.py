#!/usr/bin/python3
"""
Conftest module for pytest.

This module defines global fixtures used across multiple test modules
for the chat API application. It includes fixtures for:

- Flask test client (`client`)
- Sender instances (`sender`)
- Session instances (`session`)

Fixtures use an in-memory SQLite database for isolated testing.
"""

import pytest
import uuid
from app import create_app
from app.models.storage import init_db
from app.models.sender import Sender
from app.models.session import Session


@pytest.fixture
def client():
    """
    Provides a Flask test client with an in-memory SQLite database.

    This fixture initializes the application in TESTING mode,
    creates the database schema in memory, and yields a test client
    for making HTTP requests to the API endpoints.

    Usage in tests:
        def test_example(client):
            rv = client.get("/some-endpoint")
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    init_db()
    with app.test_client() as client:
        yield client


@pytest.fixture
def sender():
    """
    Provides a test Sender instance stored in the database.

    Creates a sender with a unique email and a default password.
    Ensures the sender is added to the database before yielding,
    and deletes it after the test completes.

    Usage in tests:
        def test_sender_example(sender):
            assert sender.email.startswith("test_")
    """
    s = Sender(email=f"test_{uuid.uuid4()}@example.com")
    s.set_password("1234")
    from app.models.storage import new, delete

    new(s)
    yield s
    delete(s)


@pytest.fixture
def session(sender):
    """
    Provides a test Session instance linked to a sender.

    Creates a session for the provided sender, stores it in the database,
    and ensures it is deleted after the test completes.

    Usage in tests:
        def test_session_example(session):
            assert session.user_id == sender.id
    """
    sess = Session(user_id=sender.id)
    from app.models.storage import new, delete

    new(sess)
    yield sess
    delete(sess)
