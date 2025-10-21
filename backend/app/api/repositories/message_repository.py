#!/usr/bin/env python3
"""
Message Repository Layer
------------------------

This module provides a simple abstraction layer for database operations
related to the `Message` model.

The repository isolates direct database interactions from the service layer,
allowing for cleaner, more maintainable, and testable code.

Classes:
    MessageRepository: Handles message persistence and retrieval from storage.
"""

from app.models.message import Message
from app.models import storage


class MessageRepository:
    """
    Repository class for managing CRUD operations
    related to `Message` entities.

    This class abstracts the storage logic, making
    the service layer independent
    of the underlying database engine or ORM configuration.
    """

    @staticmethod
    def create(msg: Message):
        """
        Persist a new message instance in the database.

        Args:
            msg (Message): A `Message` object to be stored.

        Returns:
            Message: The same `Message` instance after
            being committed to the database.
        """
        storage.new(msg)
        return msg

    @staticmethod
    def list_by_session(
                        session_id: str,
                        limit: int = 50,
                        offset: int = 0,
                        sender: str = None
                        ):
        """
        Retrieve messages associated with a given session.

        This method performs an in-memory filter of all messages
        (suitable for testing or lightweight usage).
        It is not optimized for production-scale datasets.

        Args:
            session_id (str): The unique identifier of the chat session.
            limit (int, optional): Maximum number of
            messages to return. Defaults to 50.
            offset (int, optional): Number of messages to
            skip (for pagination). Defaults to 0.
            sender (str, optional): Optional filter for sender ID or type.

        Returns:
            list[Message]: A list of `Message` objects matching the criteria.
        """
        all_msgs = list(storage.all(Message).values())
        filtered = [m for m in all_msgs if m.session_id == session_id]

        if sender:
            filtered = [
                m for m in filtered
                if getattr(m, "sender_id", None) == sender
            ]

        # Sort messages by timestamp (oldest first)
        filtered.sort(key=lambda x: x.timestamp)

        # Apply pagination
        return filtered[offset: offset + limit]
