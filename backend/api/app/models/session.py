#!/usr/bin/python3
"""
Session model module.

This module defines the `Session` class, representing chat sessions within
the application. Each session is associated with a specific sender (user)
and includes metadata such as title, creation time, and update time.

Classes:
    Session: Represents a chat session in the database.
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base_model import Base, BaseModel


class Session(BaseModel, Base):
    """
    Represents a chat session record in the database.

    This model extends `BaseModel` to inherit common attributes like
    `id`, `created_at`, and `updated_at`. Each session has a unique
    session identifier (`session_id`) and is linked to a sender (`user_id`).

    Attributes:
        __tablename__ (str): Name of the table in the database ("sessions").
        session_id (str): Unique UUID string identifying the session.
        user_id (str): Foreign key referencing the sender who owns the session.
        title (str): Optional title or description of the session.
    """

    __tablename__ = "sessions"

    session_id = Column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        doc="Unique UUID for the chat session."
    )
    user_id = Column(
        String(60),
        ForeignKey("senders.id"),
        nullable=False,
        doc="Foreign key linking the session to its sender (user)."
    )
    title = Column(
        String(256),
        nullable=True,
        doc="Optional session title or short description."
    )
