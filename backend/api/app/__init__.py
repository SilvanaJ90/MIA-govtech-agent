#!/usr/bin/env python3
"""
Application factory module.

This module defines the `create_app` function, which initializes and configures
the Flask application instance.
to create modular, testable, and maintainable applications.

Responsibilities:
    - Initialize Flask application.
    - Load configuration from the `Config` class.
    - Initialize the database and create tables if needed.
    - Register API blueprints.
    - Register custom error handlers.
    - Initialize Swagger for API documentation.
"""

from flask import Flask
from app.api import register_blueprints
from app.config import Config
from app.models import storage
from app.api.errors import register_error_handlers
from flasgger import Swagger
from app.models.storage import init_db, preload_test_data


def create_app():
    """
    Application factory function.

    Creates and configures a Flask application instance
    using the factory pattern.
    This allows for flexible configurations,
    easier testing, and modular design.

    Returns:
        Flask: The fully configured Flask application instance.
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration settings from the Config class
    app.config.from_object(Config)

    # Initialize the database (create tables if they don’t exist)

    init_db()

    # Pre-cargar sender, session y mensaje
    preload_test_data()

    # Register all API blueprints
    register_blueprints(app)

    # Register global error handlers
    register_error_handlers(app)

    # Initialize Swagger for interactive API documentation
    Swagger(app)

    return app
