"""Configuration loader for the bot."""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.
    
    Looks for .env.bot.secret in the bot directory (VM/local) or parent directory (project root).
    Returns a dict with all required configuration values.
    """
    # Try to load from bot directory first, then parent
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"
    if not env_file.exists():
        env_file = bot_dir.parent / ".env.bot.secret"
    
    if env_file.exists():
        load_dotenv(env_file)
    
    config = {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_BASE_URL": os.getenv("LMS_API_BASE_URL", "http://localhost:42002"),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", "coder-model"),
    }
    
    return config
