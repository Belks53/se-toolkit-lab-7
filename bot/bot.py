#!/usr/bin/env python3
"""LMS Telegram Bot - Entry point.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test CMD   # Test mode (no Telegram connection)
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_natural_language,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="CMD",
        help="Test mode: run a command and print output (no Telegram connection)"
    )
    return parser.parse_args()


async def run_test_command(command: str, config: dict) -> str:
    """Run a command in test mode and return the output.
    
    Args:
        command: The command to run (e.g., "/start", "/help", "/health")
        config: Configuration dictionary
        
    Returns:
        The response text
    """
    # Parse command and arguments
    parts = command.strip().split()
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd == "/start":
        return await handle_start()
    elif cmd == "/help":
        return await handle_help()
    elif cmd == "/health":
        return await handle_health(
            config["LMS_API_BASE_URL"],
            config["LMS_API_KEY"]
        )
    elif cmd == "/labs":
        return await handle_labs(
            config["LMS_API_BASE_URL"],
            config["LMS_API_KEY"]
        )
    elif cmd == "/scores":
        if len(args) < 1:
            return "Usage: /scores <lab_name>\nExample: /scores lab-04"
        return await handle_scores(
            args[0],
            config["LMS_API_BASE_URL"],
            config["LMS_API_KEY"]
        )
    else:
        # Treat as natural language query
        return await handle_natural_language(command)


async def run_telegram_bot(config: dict):
    """Run the Telegram bot.
    
    Args:
        config: Configuration dictionary with BOT_TOKEN and other settings
    """
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
    except ImportError:
        print("Error: aiogram not installed. Run 'uv sync' in the bot directory.")
        sys.exit(1)
    
    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN not set. Check .env.bot.secret")
        sys.exit(1)
    
    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()
    
    # Command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        response = await handle_start()
        await message.answer(response)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = await handle_help()
        await message.answer(response)
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        response = await handle_health(
            config["LMS_API_BASE_URL"],
            config["LMS_API_KEY"]
        )
        await message.answer(response)
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = await handle_labs(
            config["LMS_API_BASE_URL"],
            config["LMS_API_KEY"]
        )
        await message.answer(response)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message, command: types.Command):
        lab_name = command.args.strip() if command.args else ""
        if not lab_name:
            response = "Usage: /scores <lab_name>\nExample: /scores lab-04"
        else:
            response = await handle_scores(
                lab_name,
                config["LMS_API_BASE_URL"],
                config["LMS_API_KEY"]
            )
        await message.answer(response)
    
    @dp.message()
    async def handle_message(message: types.Message):
        """Handle natural language messages."""
        response = await handle_natural_language(message.text)
        await message.answer(response)
    
    # Start polling
    print("Bot is starting...")
    await dp.start_polling(bot)


async def main():
    """Main entry point."""
    args = parse_args()
    config = load_config()
    
    if args.test:
        # Test mode - run command and print output
        result = await run_test_command(args.test, config)
        print(result)
        sys.exit(0)
    else:
        # Normal mode - run Telegram bot
        await run_telegram_bot(config)


if __name__ == "__main__":
    asyncio.run(main())
