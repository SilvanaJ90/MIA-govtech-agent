"""
API package initializer.

This module is responsible for registering all
API blueprints with the Flask application.
Each blueprint represents a logical grouping
of routes, such as messages, users, or sessions.

You can define global prefixes (e.g., `/api`)
to manage different versions of your API.
"""

from .controllers.messages import bp as messages_bp


def register_blueprints(app):
    """
    Register all API blueprints with the given Flask application instance.

    Args:
        app (Flask): The Flask application where blueprints will be registered.
    """
    # Register the messages blueprint under the /api/messages prefix
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
