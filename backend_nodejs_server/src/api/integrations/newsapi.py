from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from src.api.core.config import settings
from src.api.utils.cache import SimpleRateLimiter, TTLCache

_cache = TTLCache()
_rl = SimpleRateLimiter()


class NewsApiClient:
    """Client wrapper for NewsAPI endpoints used by the app."""

    def _api_key(self) -> str:
        if not settings.newsapi_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="NEWSAPI_KEY is not configured",
            )
        return settings.newsapi_key

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"https://newsapi.org/v2/{path.lstrip('/')}"
        merged = dict(params or {})
        merged["apiKey"] = self._api_key()

        cache_key = f"newsapi:{url}:{merged}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        if not _rl.allow("newsapi", settings.rate_limit_window_s, settings.rate_limit_max):
            raise HTTPException(status_code=429, detail="Rate limit exceeded (server protection)")

        timeout = httpx.Timeout(20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.get(url, params=merged, timeout=timeout)
            except httpx.HTTPError:
                raise HTTPException(status_code=502, detail="Upstream NewsAPI network error")

        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Upstream NewsAPI error: {resp.status_code}")

        data = resp.json()
        _cache.set(cache_key, data, ttl_s=max(60, settings.cache_ttl_s))
        return data

    # PUBLIC_INTERFACE
    async def top_headlines(self, query: str = "football", page_size: int = 20) -> Dict[str, Any]:
        """Fetch top headlines for football."""
        return await self._get(
            "top-headlines",
            params={
                "q": query,
                "language": "en",
                "pageSize": page_size,
            },
        )


client = NewsApiClient()
