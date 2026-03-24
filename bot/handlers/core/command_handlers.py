"""Command handlers for the LMS bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - this makes them testable without the Telegram API.
"""


async def handle_start() -> str:
    """Handle /start command - welcome message."""
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you interact with the LMS backend through chat.\n\n"
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - List all commands\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Get scores for a lab\n\n"
        "You can also ask me questions in plain language!"
    )


async def handle_help() -> str:
    """Handle /help command - list available commands."""
    return (
        "📖 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check if the LMS backend is up\n"
        "/labs - List all available labs\n"
        "/scores <lab_name> - Get pass rates for a specific lab\n\n"
        "You can also ask questions in natural language, like:\n"
        "• 'What labs are available?'\n"
        "• 'Show me the health status'\n"
        "• 'What are my scores for lab-04?'"
    )


async def handle_health(lms_api_url: str, lms_api_key: str) -> str:
    """Handle /health command - check backend status.

    Args:
        lms_api_url: Base URL of the LMS API
        lms_api_key: API key for authentication

    Returns:
        Status message indicating if backend is up or down
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            # Check if backend is up by trying to access /items/ endpoint
            response = await client.get(
                f"{lms_api_url}/items/",
                headers={"Authorization": f"Bearer {lms_api_key}"},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                item_count = len(data) if isinstance(data, list) else "unknown"
                return f"✅ Backend is UP and running! {item_count} items available."
            elif response.status_code == 502:
                return f"⚠️ Backend returned status 502 Bad Gateway. The backend service may be down."
            else:
                return f"⚠️ Backend returned status {response.status_code}. Check the backend logs."
    except httpx.ConnectError as e:
        return f"❌ Backend connection refused ({lms_api_url}). Check that the services are running."
    except httpx.ReadTimeout:
        return f"❌ Backend timed out ({lms_api_url}). The service may be overloaded."
    except Exception as e:
        return f"❌ Backend error: {str(e)}. Check that the backend is running."


async def handle_labs(lms_api_url: str, lms_api_key: str) -> str:
    """Handle /labs command - list available labs.

    Args:
        lms_api_url: Base URL of the LMS API
        lms_api_key: API key for authentication

    Returns:
        Formatted list of available labs
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{lms_api_url}/items/",
                headers={"Authorization": f"Bearer {lms_api_key}"},
                timeout=10.0
            )
            if response.status_code == 200:
                items_data = response.json()
                # Filter for labs (type == "lab")
                if isinstance(items_data, list):
                    labs = [item for item in items_data if item.get("type") == "lab"]
                    if labs:
                        labs_list = "\n".join([f"• {lab.get('title', lab.get('name', 'Unknown'))}" for lab in labs])
                        return f"📚 Available Labs:\n\n{labs_list}"
                    else:
                        return "📚 No labs available at the moment."
                else:
                    return "📚 No labs available at the moment."
            else:
                return f"⚠️ Failed to fetch labs (status {response.status_code})"
    except httpx.ConnectError:
        return "❌ Cannot connect to backend - is the LMS API running?"
    except Exception as e:
        return f"❌ Error fetching labs: {str(e)}"


async def handle_scores(lab_name: str, lms_api_url: str, lms_api_key: str) -> str:
    """Handle /scores command - get scores for a lab.

    Args:
        lab_name: Name of the lab to get scores for
        lms_api_url: Base URL of the LMS API
        lms_api_key: API key for authentication

    Returns:
        Formatted scores information
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            # Use the pass-rates endpoint with lab query parameter
            response = await client.get(
                f"{lms_api_url}/analytics/pass-rates?lab={lab_name}",
                headers={"Authorization": f"Bearer {lms_api_key}"},
                timeout=10.0
            )
            if response.status_code == 200:
                scores_data = response.json()
                if scores_data:
                    # Format the pass rates data nicely
                    lines = []
                    for task in scores_data:
                        task_name = task.get("task", "Unknown")
                        avg_score = task.get("avg_score", 0)
                        attempts = task.get("attempts", 0)
                        lines.append(f"• {task_name}: {avg_score}% avg ({attempts} attempts)")
                    return f"📊 Pass rates for {lab_name}:\n\n" + "\n".join(lines)
                else:
                    return f"⚠️ No scores found for '{lab_name}'"
            else:
                return f"⚠️ No scores found for '{lab_name}' (status {response.status_code})"
    except httpx.ConnectError:
        return "❌ Cannot connect to backend - is the LMS API running?"
    except Exception as e:
        return f"❌ Error fetching scores: {str(e)}"


async def handle_natural_language(
    query: str,
    lms_api_url: str = "",
    lms_api_key: str = "",
    llm_api_key: str = "",
    llm_api_base_url: str = "",
    llm_api_model: str = "",
) -> str:
    """Handle natural language queries using LLM-powered intent routing.

    Args:
        query: User's natural language query
        lms_api_url: Base URL of the LMS API
        lms_api_key: API key for authentication
        llm_api_key: API key for LLM
        llm_api_base_url: Base URL for LLM API
        llm_api_model: Model name to use

    Returns:
        Response to the user's query
    """
    import httpx
    from openai import AsyncOpenAI

    from services import LMSAPIClient
    from services.intent_router import IntentRouter

    # Check if LLM is configured
    if not llm_api_key or not llm_api_base_url or llm_api_key == "<llm-api-key>" or llm_api_base_url == "<llm-api-base-url>":
        return (
            f"🤔 I received your query: '{query}'\n\n"
            "LLM integration is not configured yet. Please set up the LLM API credentials in .env.bot.secret\n\n"
            "Try these slash commands instead:\n"
            "/health - Check backend status\n"
            "/labs - List available labs\n"
            "/scores <lab> - Get scores for a lab"
        )

    try:
        # Initialize clients
        llm_client = AsyncOpenAI(
            api_key=llm_api_key,
            base_url=llm_api_base_url,
        )
        lms_client = LMSAPIClient(lms_api_url, lms_api_key)

        # Create intent router and route the query
        router = IntentRouter(llm_client, lms_client, llm_api_model)
        response = await router.route(query)

        await lms_client.close()
        return response

    except httpx.ConnectError:
        return "❌ Cannot connect to backend - is the LMS API running?"
    except Exception as e:
        error_msg = str(e)
        if "Connection error" in error_msg or "401" in error_msg:
            return "❌ LLM connection error. The Qwen Code API may need to be restarted. Try: `cd ~/qwen-code-oai-proxy && docker compose restart`"
        return f"❌ LLM error: {error_msg}"
