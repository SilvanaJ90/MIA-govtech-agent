#!/usr/bin/env python3
"""
Application configuration module.

This module defines the configuration settings for the Flask application.
It supports both environment-based configuration and default values for
local development.

Attributes:
    BASE_DIR (str): Absolute path to the current directory, used to build
                    file paths relative to the project root.
"""

import os

# Get the absolute path to the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class for the Flask application.

    This class sets up core settings such as the database URI, secret key,
    and other environment-based configurations.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): The database connection URI. It reads
            from the environment variable 'DATABASE_URL'. If not found,
            defaults to a local SQLite database (chat.db).
        SQLALCHEMY_ECHO (bool): Enables SQL query logging if set to True.
            Defaults to False for cleaner logs.
        SECRET_KEY (str): Secret key used for session management and
            security features in Flask. Reads from 'SECRET_KEY' environment
            variable or defaults to a development key.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, '..', 'chat.db')}"
    )
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
