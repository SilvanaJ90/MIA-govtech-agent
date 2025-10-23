#!/usr/bin/env python3
"""
This module provides helper functions for
basic text processing and moderation checks
within the chat message system.

Functions:
    - simple_process(content): Performs basic normalization
    and generates simple metrics.
    - contains_banned(content): Detects whether a
    message contains any banned words.

These functions are typically used before saving or analyzing messages,
ensuring text is clean and compliant with the moderation policy.
"""

from typing import Dict
from app.models.banned_word import BannedWord
from app.models import storage
from datetime import datetime, timezone


def simple_process(content: str) -> Dict:
    """
    Perform basic text normalization and compute simple message metrics.

    Operations:
        - Trims whitespace.
        - Counts the number of words and characters.
        - Adds a UTC timestamp indicating when processing occurred.

    Args:
        content (str): The raw message content.

    Returns:
        Dict: A dictionary containing:
            - word_count (int): Total number of words in the message.
            - character_count (int): Total number of characters.
            - processed_at (str): ISO 8601 timestamp (UTC) of processing time.
    """
    txt = content.strip()
    word_count = len(txt.split())
    char_count = len(txt)
    processed_at = datetime.now(timezone.utc).isoformat()
    return {
        "word_count": word_count,
        "character_count": char_count,
        "processed_at": processed_at
    }


def contains_banned(content: str) -> bool:
    """
    Check whether the given message contains any banned words.

    This function queries the `banned_words` table from the database
    and compares each banned term against the message content
    (case-insensitive match).

    Args:
        content (str): The message text to analyze.

    Returns:
        bool: True if at least one banned word is found; otherwise, False.
    """
    banned = storage.all(BannedWord).values()
    content_lower = content.lower()
    for b in banned:
        if b.word and b.word.lower() in content_lower:
            return True
    return False
