#!/usr/bin/python3
"""
Test module for API error handlers.

This module defines pytest tests for the custom error handlers registered
in the Flask application via `register_error_handlers`. It ensures that
HTTP errors 400, 404, and 500 are properly handled and return the expected
JSON responses.

Fixtures:
    app: Provides a Flask application instance with error handlers registered.
"""

import pytest
from flask import Flask, jsonify, abort
from app.api.errors import register_error_handlers


@pytest.fixture
def app():
    """
    Provides a Flask application instance with registered error handlers.

    This fixture initializes a minimal Flask app
    and registers the application's
    custom error handlers, making it available for test client requests.
    """
    app = Flask(__name__)
    register_error_handlers(app)
    return app


def test_404_handler(app):
    """
    Test that a non-existent route triggers the 404 error handler.

    Sends a GET request to a route that does not exist and verifies that:
    - The response status code is 404.
    - The returned JSON contains the correct error code "NOT_FOUND".
    """
    client = app.test_client()
    rv = client.get("/non-existent-route")
    assert rv.status_code == 404
    data = rv.get_json()
    assert data["error"]["code"] == "NOT_FOUND"


def test_400_handler(app):
    """
    Test that manually aborting with 400 triggers the 400 error handler.

    Creates a temporary route `/bad-request`
    that calls `abort(400)` and verifies:
    - The response status code is 400.
    - The returned JSON contains the correct error code "BAD_REQUEST".
    """
    client = app.test_client()

    @app.route("/bad-request")
    def bad():
        abort(400)  # This triggers the custom error handler

    rv = client.get("/bad-request")
    assert rv.status_code == 400
    data = rv.get_json()
    assert data["error"]["code"] == "BAD_REQUEST"


def test_500_handler(app):
    """
    Test that an unhandled exception triggers the 500 error handler.

    Creates a temporary route `/server-error`
    that raises an Exception and verifies:
    - The response status code is 500.
    - The returned JSON contains the correct error code "SERVER_ERROR".
    """
    client = app.test_client()

    @app.route("/server-error")
    def err():
        raise Exception("boom")  # Simulate server-side error

    rv = client.get("/server-error")
    assert rv.status_code == 500
    data = rv.get_json()
    assert data["error"]["code"] == "SERVER_ERROR"
