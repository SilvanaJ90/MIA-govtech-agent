"""
schemas.py
-----------
This module defines the data validation and serialization schemas
used by the API endpoints for message processing.

It leverages Pydantic models to ensure type safety, validation,
and consistent API responses.

Classes:
    - MessageIn: Schema for incoming messages (request payload).
    - MessageOut: Schema for outgoing messages (response format).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class MessageIn(BaseModel):
    """
    Schema representing the payload for creating or receiving a message.
    """

    message_id: Optional[str] = None
    session_id: Optional[str] = None
    content: str
    timestamp: Optional[datetime] = None
    sender_id: Optional[str] = None
    # Expected values: "user" | "system" | "bot"
    sender_type: Optional[str] = None

    @field_validator(("sender_type"))
    def sender_type_must_be_valid(cls, v):
        """
        Validate that sender_type, if provided, is one of the allowed values.
        """
        if v is None:
            return v
        if v not in ("user", "system", "bot"):
            raise ValueError("sender_type must be 'user', 'system', or 'bot'")
        return v

    @field_validator(("content"))
    def content_not_empty(cls, v):
        """
        Ensure the message content is a non-empty string.
        """
        if not isinstance(v, str) or not v.strip():
            raise ValueError("content must not be empty")
        return v.strip()


class MessageOut(BaseModel):
    """
    Schema representing the structure of a message returned by the API.

    Attributes:
        message_id (str): Unique identifier of the message (UUID).
        session_id (str): Identifier of the session the message belongs to.
        content (str): Text content of the message.
        timestamp (datetime): Timestamp when the message was created.
        sender (str): Name or type of the sender (e.g., user, system, bot).
        metadata (dict): Additional data related to the message, if any.
    """

    message_id: str
    session_id: str
    content: str
    timestamp: datetime
    sender: str
    metadata: dict
