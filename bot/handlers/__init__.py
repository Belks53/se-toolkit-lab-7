"""Command handlers for the LMS bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - this makes them testable without the Telegram API.
"""

from .command_handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_natural_language,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_natural_language",
]
