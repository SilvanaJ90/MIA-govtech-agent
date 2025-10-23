#!/usr/bin/env python3
"""
Base model module.

This module defines the BaseModel class,
which serves as the abstract base class
for all SQLAlchemy models in the application.
It provides common attributes such as
`id`, `created_at`, and `updated_at`,
along with helper methods for object
serialization and string representation.

Classes:
    BaseModel: Abstract base class for all database models.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

# SQLAlchemy declarative base for all ORM models
Base = declarative_base()

# Standard datetime format used across the application
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class BaseModel:
    """
    Abstract base class for all SQLAlchemy models.

    This class provides:
        - A unique string-based UUID as the primary key (`id`).
        - Timestamps for creation and last update.
        - A method to serialize model instances into dictionaries.
        - A readable string representation for debugging and logging.

    Attributes:
        id (str): Unique identifier for the record (UUID format).
        created_at (datetime): Timestamp for when the record was created.
        updated_at (datetime): Timestamp for the last record update.
    """

    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __init__(self, *args, **kwargs):
        """
        Initializes a new BaseModel instance.

        Automatically generates a UUID if `id` is not provided and sets
        `created_at` and `updated_at` timestamps using the current UTC time.

        Args:
            *args: Variable positional arguments for SQLAlchemy.
            **kwargs: Optional model attributes for initialization.
        """
        super().__init__(*args, **kwargs)
        if not getattr(self, "id", None):
            self.id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        if not getattr(self, "created_at", None):
            self.created_at = kwargs.get("created_at", now)
        if not getattr(self, "updated_at", None):
            self.updated_at = kwargs.get("updated_at", now)

    def to_dict(self):
        """
        Serializes the model instance into a dictionary.

        Returns:
            dict: A dictionary representation of the model,
                  including class name and formatted timestamps.
        """
        d = dict(self.__dict__)
        d.pop("_sa_instance_state", None)
        d["__class__"] = self.__class__.__name__
        if isinstance(self.created_at, datetime):
            d["created_at"] = self.created_at.strftime(TIME_FORMAT)
        if isinstance(self.updated_at, datetime):
            d["updated_at"] = self.updated_at.strftime(TIME_FORMAT)
        return d

    def __repr__(self):
        """
        Returns a readable string representation of the model instance.

        Returns:
            str: A formatted string containing the class name and record ID.
        """
        return f"[{self.__class__.__name__}] ({self.id})"
