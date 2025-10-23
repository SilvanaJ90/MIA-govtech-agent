#!/usr/bin/python3
"""
BannedWord model module.

This module defines the `BannedWord` class, which represents words or phrases
that are prohibited within the chat system. The model is used to identify and
filter restricted content in messages.

Classes:
    BannedWord: SQLAlchemy model representing a banned or restricted word.
"""

from sqlalchemy import Column, String
from .base_model import Base, BaseModel


class BannedWord(BaseModel, Base):
    """
    Represents a banned or restricted word in the database.

    This model inherits from `BaseModel`, which provides standard attributes
    such as `id`, `created_at`, and `updated_at`. Each record corresponds
    to a word that is not allowed in user messages.

    Attributes:
        __tablename__ (str): Name of the table ("banned_words").
        word (str): The restricted word or phrase.
    """

    __tablename__ = "banned_words"

    word = Column(
        String(128),
        unique=True,
        nullable=False,
        doc="The word or phrase that is prohibited in the chat system."
    )
