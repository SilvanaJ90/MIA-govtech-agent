#!/usr/bin/python3
"""
Sender model module.

This module defines the `Sender` class, which represents users, bots, or system
entities that can send or receive messages within the chat application.

It includes authentication-related methods for securely handling passwords,
as well as an enumeration class to categorize different sender types.
"""

from sqlalchemy import Column, String, Boolean, Enum
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import Base, BaseModel
import enum


class SenderType(enum.Enum):
    """
    Enumeration of sender types.

    Defines the possible categories for a sender within the chat system.

    Attributes:
        USER (str): Represents a human user.
        SYSTEM (str): Represents a system-level sender.
        BOT (str): Represents an automated bot sender.
    """

    USER = "user"
    SYSTEM = "system"
    BOT = "bot"


class Sender(BaseModel, Base):
    """
    Represents a sender (user, bot, or system) in the database.

    This model inherits from `BaseModel` to include standard attributes
    such as `id`, `created_at`, and `updated_at`. It also manages user
    authentication via password hashing.

    Attributes:
        __tablename__ (str): Name of the table ("senders").
        email (str): Unique email address of the sender.
        password_hash (str): Hashed password for authentication.
        first_name (str): First name of the sender.
        last_name (str): Last name of the sender.
        is_active (bool): Indicates whether the sender’s account is active.
        type (SenderType): Type of sender (user, system, or bot).
    """

    __tablename__ = "senders"

    email = Column(String(128), unique=True, nullable=True)
    password_hash = Column(String(256), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    type = Column(Enum(SenderType, values_callable=lambda obj: [e.value for e in obj]), 
    default=SenderType.USER, 
    nullable=False
)

    @property
    def password(self):
        """
        Prevents direct access to the plain password.

        Raises:
            AttributeError: Always, since passwords are write-only.
        """
        raise AttributeError("Password is not readable")

    def set_password(self, password: str):
        """
        Hashes and sets the sender's password securely.

        Args:
            password (str): Plaintext password to be hashed and stored.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verifies whether a given password matches the stored hash.

        Args:
            password (str): Plaintext password to validate.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
