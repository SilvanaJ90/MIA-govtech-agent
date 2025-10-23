#!/usr/bin/env python3
"""
Error Handlers Module
---------------------

This module defines global error handlers for the Flask application.
It ensures that all errors return consistent JSON
responses instead of HTML pages.

Each handler captures a specific HTTP error and returns a structured
JSON response containing a status, an error code, and a message.

Functions:
    register_error_handlers(app): Registers all custom
    error handlers for the given Flask app.
"""

from flask import jsonify


def register_error_handlers(app):
    """
    Register global error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None: This function modifies the Flask app
        by adding custom error handlers.

    Handled Errors:
        - 400: Bad Request (invalid or malformed request)
        - 404: Not Found (resource or endpoint not found)
        - 500: Internal Server Error (unexpected server-side error)
    """

    @app.errorhandler(400)
    def bad_request(e):
        """Handle HTTP 400 Bad Request errors."""
        return jsonify({
            "status": "error",
            "error": {
                "code": "BAD_REQUEST",
                "message": str(e)
            }
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        """Handle HTTP 404 Not Found errors."""
        return jsonify({
            "status": "error",
            "error": {
                "code": "NOT_FOUND",
                "message": str(e)
            }
        }), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle HTTP 500 Internal Server Error responses."""
        return jsonify({
            "status": "error",
            "error": {
                "code": "SERVER_ERROR",
                "message": "Internal server error"
            }
        }), 500
