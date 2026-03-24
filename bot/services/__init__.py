"""Service layer for external API clients."""
import httpx
from openai import AsyncOpenAI


class LMSAPIClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def get_items(self) -> list:
        """Get list of all items (labs and tasks)."""
        response = await self._client.get(f"{self.base_url}/items/")
        if response.status_code == 200:
            return response.json()
        return []

    async def get_learners(self) -> list:
        """Get list of enrolled learners."""
        response = await self._client.get(f"{self.base_url}/learners/")
        if response.status_code == 200:
            return response.json()
        return []

    async def get_scores(self, lab: str) -> list:
        """Get score distribution for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/scores",
            params={"lab": lab}
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_pass_rates(self, lab: str) -> list:
        """Get per-task pass rates for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/pass-rates",
            params={"lab": lab}
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_timeline(self, lab: str) -> list:
        """Get submission timeline for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/timeline",
            params={"lab": lab}
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_groups(self, lab: str) -> list:
        """Get per-group performance for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/groups",
            params={"lab": lab}
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_top_learners(self, lab: str, limit: int = 10) -> list:
        """Get top learners for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/top-learners",
            params={"lab": lab, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        return []

    async def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        response = await self._client.get(
            f"{self.base_url}/analytics/completion-rate",
            params={"lab": lab}
        )
        if response.status_code == 200:
            return response.json()
        return {}

    async def trigger_sync(self) -> dict:
        """Trigger ETL pipeline sync."""
        response = await self._client.post(
            f"{self.base_url}/pipeline/sync",
            json={}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Status {response.status_code}"}


class LLMClient:
    """Client for interacting with the LLM API."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    async def chat(self, messages: list[dict]) -> str:
        """Send a chat message and get response."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
