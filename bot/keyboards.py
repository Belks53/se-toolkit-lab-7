"""Inline keyboard definitions for Telegram bot.

These are Telegram-specific UI elements for quick actions.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard with quick action buttons.

    Returns:
        InlineKeyboardMarkup with common query buttons
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 What labs are available?",
                    callback_data="query_what_labs"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💪 Show scores for lab-04",
                    callback_data="query_scores_lab04"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Top 5 students in lab-04",
                    callback_data="query_top5_lab04"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Which lab has lowest pass rate?",
                    callback_data="query_lowest_pass_rate"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Check backend health",
                    callback_data="query_health"
                ),
            ],
        ]
    )
    return keyboard


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Create a help keyboard with command buttons.

    Returns:
        InlineKeyboardMarkup with command buttons
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="/health", callback_data="cmd_health"),
                InlineKeyboardButton(text="/labs", callback_data="cmd_labs"),
            ],
            [
                InlineKeyboardButton(text="/scores lab-01", callback_data="cmd_scores_lab01"),
                InlineKeyboardButton(text="/scores lab-04", callback_data="cmd_scores_lab04"),
            ],
        ]
    )
    return keyboard
