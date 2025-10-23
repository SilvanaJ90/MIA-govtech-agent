#!/usr/bin/env python3
"""
Database storage module.

This module manages database connections, sessions, and common CRUD operations
using SQLAlchemy. It provides helper functions to interact with the database
without needing to directly manage sessions in other parts of the application.

Responsibilities:
    - Initialize the database engine and session.
    - Create tables from SQLAlchemy models.
    - Provide helper functions for basic CRUD operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.config import Config
from .base_model import Base
from datetime import datetime
import os

# Import models for preloading
from app.models.sender import Sender
from app.models.session import Session
from app.models.message import Message

# Create the SQLAlchemy engine using the application's database URI
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)

# Thread-safe session factory
SessionLocal = scoped_session(sessionmaker(bind=engine))


def init_db():
    """
    Initializes the database by creating all tables
    defined in the Base metadata.
    This function should be called once at application startup.
    """
    Base.metadata.create_all(engine)


# -------------------------------------------------------------------------
# Simple storage helper functions
# -------------------------------------------------------------------------

def new(obj):
    """
    Adds a new object to the database and commits the transaction.

    Args:
        obj (BaseModel): The SQLAlchemy model instance to be added.
    """
    db = SessionLocal()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    db.close()


def save():
    """
    Commits the current transaction and closes the session.
    Used to persist changes made to existing objects.
    """
    db = SessionLocal()
    db.commit()
    db.close()


def delete(obj):
    """
    Deletes an object from the database and commits the transaction.

    Args:
        obj (BaseModel): The SQLAlchemy model instance to be deleted.
    """
    db = SessionLocal()
    db.delete(obj)
    db.commit()
    db.close()


def all(model_cls):
    """
    Retrieves all records of a given model class.

    Args:
        model_cls (class): The SQLAlchemy model class to query.

    Returns:
        dict: A dictionary of model instances, keyed by their unique ID.
    """
    with SessionLocal() as db:
        items = db.query(model_cls).all()
        return {i.id: i for i in items}


def get(model_cls, id_):
    """
    Retrieves a single record by its ID.

    Args:
        model_cls (class): The SQLAlchemy model class to query.
        id_ (str): The unique identifier of the record.

    Returns:
        BaseModel | None: The model instance if found, otherwise None.
    """
    with SessionLocal() as db:
        obj = db.get(model_cls, id_)
        return obj


# -------------------------------------------------------------------------
# Preload test data for API usage
# -------------------------------------------------------------------------
def preload_test_data():
    """Carga sender, session y mensaje de prueba en la base de datos."""

    # Crear sender si no existe
    sender_id = "sender_1"
    if sender_id not in [s.id for s in all(Sender).values()]:
        sender = Sender(
            id=sender_id,
            email="user1@example.com",
            first_name="User",
            last_name="One",
            type="user",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new(sender)

    # Crear sesión si no existe
    session_id = "sess_123456"
    if session_id not in [s.session_id for s in all(Session).values()]:
        session = Session(
            session_id=session_id,
            user_id=sender_id,
            title="Chat de prueba",
            id="sess_id_1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new(session)

    # Crear mensaje de prueba si no existe
    message_id = "msg_001"
    if message_id not in [m.message_id for m in all(Message).values()]:
        msg = Message(
            message_id=message_id,
            session_id=session_id,
            sender_id=sender_id,
            content="Hola, este es un mensaje de prueba",
            timestamp=datetime.now(),
            id="msg_id_1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new(msg)
