#!/usr/bin/python3
"""
Message model module.

This module defines the `Message` class, which represents individual chat
messages exchanged within a session. Each message is linked to a session
and a sender, and can include additional metadata in JSON format.

Classes:
    Message: SQLAlchemy model representing a chat message.
"""

import uuid
import json
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base_model import Base, BaseModel


class Message(BaseModel, Base):
    """
    Represents a chat message record in the database.

    Each message is associated with a specific session and sender.
    The model also supports storing structured metadata as JSON.

    Attributes:
        __tablename__ (str): Name of the table ("messages").
        message_id (str): Unique identifier (UUID) for the message.
        session_id (str): Foreign key linking the message to its session.
        sender_id (str): Foreign key linking the message to the sender.
        content (str): Main text content of the message.
        timestamp (datetime): Timestamp for when the message was created.
        metadata_json (str): Optional JSON-formatted string for metadata.
    """

    __tablename__ = "messages"

    message_id = Column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        doc="Unique UUID string identifying the message."
    )
    session_id = Column(
        String(36),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key referencing the chat session this message belongs to."
    )
    sender_id = Column(
        String(60),
        ForeignKey("senders.id"),
        nullable=False,
        doc="Foreign key referencing the sender of this message."
    )
    content = Column(
        Text,
        nullable=False,
        doc="Text content of the message."
    )
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp indicating when the message was created (UTC)."
    )
    metadata_json = Column(
        Text,
        nullable=True,
        doc="Optional metadata stored as a JSON string."
    )

    def set_metadata(self, data: dict):
        """
        Stores metadata as a JSON string in the database.

        Args:
            data (dict): A dictionary containing metadata
            related to the message.
        """
        self.metadata_json = json.dumps(data)

    def get_metadata(self):
        """
        Retrieves metadata as a Python dictionary.

        Returns:
            dict: Parsed metadata if available, otherwise an empty dictionary.
        """
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
