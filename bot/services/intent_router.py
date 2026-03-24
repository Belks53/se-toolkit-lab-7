"""LLM-powered intent router for natural language queries.

This module implements the tool-calling loop:
1. Send user message + tool definitions to LLM
2. LLM returns tool calls
3. Execute tools against backend
4. Feed results back to LLM
5. LLM summarizes the answer
"""
import json
import sys
from typing import Any

from openai import AsyncOpenAI


# Tool definitions for all 9 backend endpoints
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this first to discover what's available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets: 0-25, 26-50, 51-75, 76-100) for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab to see activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by average score for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return (default: 10)"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate (percentage of learners who scored >= 60) for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline sync to refresh data from autochecker. Use when data seems stale.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System (LMS). 
You have access to tools that query the backend API. Your job is to:

1. Understand the user's question
2. Call the appropriate tools to get data
3. Analyze the results
4. Provide a clear, helpful answer based on the data

Guidelines:
- Always call tools to get real data before answering
- If the user asks about a specific lab, use the lab identifier they provided (e.g., "lab-04")
- If the user says "lab 4" or "lab four", convert it to "lab-04" format
- For comparisons (e.g., "which lab is best"), you may need to call tools multiple times
- If you don't have enough information, ask for clarification
- If the user greets you, respond warmly and mention what you can help with
- If the user's message is unclear, politely ask for clarification

Available tools:
- get_items: List all labs and tasks
- get_pass_rates: Get per-task scores for a lab
- get_scores: Get score distribution for a lab
- get_timeline: Get submission activity over time
- get_groups: Get per-group performance
- get_top_learners: Get top students leaderboard
- get_completion_rate: Get percentage of students who passed
- get_learners: Get enrolled students list
- trigger_sync: Refresh data from autochecker
"""


class IntentRouter:
    """Routes natural language queries to backend tools via LLM."""

    def __init__(self, llm_client: AsyncOpenAI, lms_api_client, model: str):
        self.llm_client = llm_client
        self.lms_api_client = lms_api_client
        self.model = model

    async def route(self, user_message: str) -> str:
        """Route a user message through the LLM tool-calling loop.

        Args:
            user_message: The user's natural language query

        Returns:
            The final response to show to the user
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5
        for iteration in range(max_iterations):
            # Call LLM
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            choice = response.choices[0]
            assistant_message = choice.message

            # Check if LLM wants to call tools
            if not assistant_message.tool_calls:
                # No tool calls - LLM is ready to answer
                return assistant_message.content or "I'm not sure how to help with that."

            # Execute tool calls
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Log for debugging
                print(f"[tool] LLM called: {function_name}({function_args})", file=sys.stderr)

                # Execute the tool
                result = await self._execute_tool(function_name, function_args)
                result_str = json.dumps(result) if not isinstance(result, str) else result

                print(f"[tool] Result: {result_str[:200]}{'...' if len(result_str) > 200 else ''}", file=sys.stderr)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })

            print(f"[summary] Feeding {len(assistant_message.tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        # If we get here, we hit max iterations
        return "I'm having trouble processing your request. Please try rephrasing."

    async def _execute_tool(self, name: str, args: dict[str, Any]) -> Any:
        """Execute a tool by calling the appropriate backend endpoint.

        Args:
            name: The tool name
            args: The tool arguments

        Returns:
            The tool result
        """
        if name == "get_items":
            return await self.lms_api_client.get_items()
        elif name == "get_learners":
            return await self.lms_api_client.get_learners()
        elif name == "get_scores":
            return await self.lms_api_client.get_scores(args.get("lab", ""))
        elif name == "get_pass_rates":
            return await self.lms_api_client.get_pass_rates(args.get("lab", ""))
        elif name == "get_timeline":
            return await self.lms_api_client.get_timeline(args.get("lab", ""))
        elif name == "get_groups":
            return await self.lms_api_client.get_groups(args.get("lab", ""))
        elif name == "get_top_learners":
            return await self.lms_api_client.get_top_learners(
                args.get("lab", ""),
                args.get("limit", 10)
            )
        elif name == "get_completion_rate":
            return await self.lms_api_client.get_completion_rate(args.get("lab", ""))
        elif name == "trigger_sync":
            return await self.lms_api_client.trigger_sync()
        else:
            return {"error": f"Unknown tool: {name}"}
