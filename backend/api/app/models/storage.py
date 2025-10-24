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




