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
    
    async def get_health(self) -> dict:
        """Check backend health status."""
        response = await self._client.get(f"{self.base_url}/health")
        return {"status_code": response.status_code, "ok": response.status_code == 200}
    
    async def get_labs(self) -> list:
        """Get list of available labs."""
        response = await self._client.get(f"{self.base_url}/labs")
        if response.status_code == 200:
            return response.json()
        return []
    
    async def get_scores(self, lab_name: str) -> dict:
        """Get scores for a specific lab."""
        response = await self._client.get(f"{self.base_url}/analytics/{lab_name}")
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
