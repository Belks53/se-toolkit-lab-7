# Development Plan — LMS Telegram Bot

## Overview

This document outlines the development plan for building a Telegram bot that enables users to interact with the LMS (Learning Management System) backend through natural language chat. The bot will provide both command-based interactions (`/start`, `/help`, `/health`, `/labs`, `/scores`) and natural language understanding powered by an LLM.

## Architecture

The bot follows a layered architecture:

1. **Entry Point (`bot.py`)**: Handles both Telegram bot mode and CLI test mode. The `--test` flag allows running commands without a Telegram connection, which is essential for automated testing and local development.

2. **Handlers Layer (`handlers/`)**: Pure functions that implement command logic. They take input parameters and return text responses without any Telegram-specific code. This separation makes handlers testable in isolation.

3. **Services Layer (`services/`)**: API clients for external services:
   - `LMSAPIClient`: Wraps HTTP calls to the LMS backend
   - `LLMClient`: Wraps calls to the LLM API for natural language processing

4. **Configuration (`config.py`)**: Loads environment variables from `.env.bot.secret` with sensible defaults.

## Task Breakdown

### Task 1: Plan and Scaffold (P0)

**Goal**: Create project structure and testable handler architecture.

- Set up `bot/` directory with proper Python package structure
- Create `pyproject.toml` with dependencies (aiogram, httpx, openai, python-dotenv)
- Implement handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Implement `--test` mode in `bot.py` for CLI testing
- Create `.env.bot.example` template
- Write this development plan

**Acceptance**: `uv run bot.py --test "/start"` prints welcome message and exits 0.

### Task 2: Backend Integration (P0)

**Goal**: Connect handlers to real LMS backend data.

- Implement `LMSAPIClient` with methods for all backend endpoints
- Update handlers to fetch real data from `/health`, `/labs`, `/analytics/{lab}`
- Add proper error handling for network failures and API errors
- Format responses with emojis and readable text
- Test against deployed backend on VM

**Acceptance**: `/health` reports actual backend status, `/labs` shows real lab list.

### Task 3: Intent-Based Natural Language Routing (P1)

**Goal**: Enable plain language queries using LLM tool use.

- Implement `LLMClient` with tool/function calling capability
- Define tools for each backend endpoint (get_health, get_labs, get_scores, etc.)
- Create intent router that parses user queries and calls appropriate tools
- Handle multi-step reasoning (LLM may chain multiple API calls)
- Add inline keyboard buttons for common actions

**Acceptance**: User can ask "what labs are available?" and get the same response as `/labs`.

### Task 4: Containerize and Deploy (P3)

**Goal**: Deploy bot alongside backend on VM.

- Create `bot/Dockerfile` for containerized deployment
- Add bot service to `docker-compose.yml`
- Configure environment variables for production
- Deploy to VM and verify bot responds in Telegram
- Document deployment process in README

**Acceptance**: Bot running on VM, responds to `/start` in Telegram.

## Testing Strategy

1. **Unit Tests**: Test handlers with mock API responses
2. **Test Mode**: Manual testing via `--test` flag before each commit
3. **Integration Tests**: Verify backend connectivity on VM
4. **Manual Testing**: Send commands to bot in Telegram

## Deployment Flow

```
Local Development → Git Push → VM Pull → Restart Bot → Test in Telegram
```

## Future Enhancements (Optional)

- Rich formatting (tables, charts as images)
- Response caching to reduce API calls
- Conversation context for multi-turn dialogues
- Flutter web chatbot interface
