#!/usr/bin/env python3
"""
Message Service Layer
---------------------

This module provides the business logic for handling chat messages.
It acts as an intermediary between the API layer
(controllers) and the data layer (repositories).

Responsibilities:
    - Validate sender and session relationships.
    - Create new chat sessions if needed.
    - Perform moderation (banned word detection).
    - Process message content to extract metadata.
    - Delegate database operations to the MessageRepository.

Classes:
    MessageService: Contains static methods
    for message creation and retrieval.
"""

from app.api.repositories.message_repository import MessageRepository
from app.models.message import Message
from app.models.session import Session
from app.models.sender import Sender
from app.models import storage
from app.api.utils.text_processing import contains_banned, simple_process


class MessageService:
    """
    Service class responsible for managing chat message operations,
    including creation, validation, and retrieval.
    """

    @staticmethod
    def create_message(payload: dict):
        """
        Create a new message record and handle its
        related session and moderation logic.

        Workflow:
            1. Validate that the sender exists.
            2. Create a new chat session if no session_id is provided.
            3. Check for banned words in the message content.
            4. Process the text and attach metadata
            (word count, timestamp, etc.).
            5. Persist the message using the repository layer.

        Args:
            payload (dict): A validated dictionary
            containing message data. Expected keys:
                - sender_id (str): ID of the
                sender (must exist in the database).
                - content (str): The text message content.
                - session_id (str, optional):
                Existing chat session ID (created if missing).

        Returns:
            tuple:
                - Message: The created message instance.
                - str: The session ID associated with this message.

        Raises:
            ValueError: If the sender or session is not found.
            PermissionError: If the content contains banned words.
        """
        sender_id = payload.get("sender_id")
        content = payload["content"]
        session_id = payload.get("session_id")

        # Validate sender existence
        sender = storage.get(Sender, sender_id)
        if not sender:
            raise ValueError("Sender not found")

        # Create or validate chat session
        if not session_id:
            # No session_id provided -> create a new Session linked to the sender
            session = Session(user_id=sender_id)
            storage.new(session)
            session_id = session.session_id
        else:
            # session_id provided -> search by the public session_id field
            session = None
            for s in storage.all(Session).values():
                if getattr(s, "session_id", None) == session_id:
                    session = s
                    break
            if not session:
                # session_id fue proporcionado pero no existe
                raise ValueError("Session not found")

        # Moderation check
        if contains_banned(content):
            raise PermissionError("Content contains banned words")

        # Create message instance
        msg = Message(
            session_id=session_id,
            sender_id=sender_id,
            content=content
        )
        metadata = simple_process(content)
        msg.set_metadata(metadata)

        # Persist message to database
        MessageRepository.create(msg)
        return msg, session_id

    @staticmethod
    def list_messages(
                        session_id: str,
                        limit: int = 50,
                        offset: int = 0,
                        sender: str = None
                        ):
        """
        Retrieve messages associated with a given session.

        Args:
            session_id (str): The unique session identifier.
            limit (int, optional): Maximum number of
            messages to return. Default is 50.
            offset (int, optional): Number of records
            to skip for pagination. Default is 0.
            sender (str, optional): Filter messages by sender ID or type.

        Returns:
            list[Message]: A list of message objects
            retrieved from the repository.
        """
        return MessageRepository.list_by_session(
            session_id, limit, offset, sender)
