from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from src.api.core.config import settings
from src.api.utils.cache import SimpleRateLimiter, TTLCache

_cache = TTLCache()
_rl = SimpleRateLimiter()


class ApiFootballClient:
    """Client wrapper for API-Football endpoints used by the app."""

    def __init__(self) -> None:
        if not settings.api_football_key:
            # Raise on use, not on import
            pass

    def _headers(self) -> Dict[str, str]:
        if not settings.api_football_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API_FOOTBALL_KEY is not configured",
            )
        return {
            "x-apisports-key": settings.api_football_key,
        }

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"https://{settings.api_football_host}/{path.lstrip('/')}"
        cache_key = f"api_football:{url}:{params}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        if not _rl.allow("api_football", settings.rate_limit_window_s, settings.rate_limit_max):
            raise HTTPException(status_code=429, detail="Rate limit exceeded (server protection)")

        timeout = httpx.Timeout(20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.get(url, headers=self._headers(), params=params)
            except httpx.HTTPError:
                raise HTTPException(status_code=502, detail="Upstream API-Football network error")

        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Upstream API-Football error: {resp.status_code}")

        data = resp.json()
        _cache.set(cache_key, data, ttl_s=settings.cache_ttl_s)
        return data

    # PUBLIC_INTERFACE
    async def fixtures_live(self) -> Dict[str, Any]:
        """Fetch live fixtures."""
        return await self._get("fixtures", params={"live": "all"})

    # PUBLIC_INTERFACE
    async def fixtures_by_date(self, date_yyyy_mm_dd: str) -> Dict[str, Any]:
        """Fetch fixtures by date (YYYY-MM-DD)."""
        return await self._get("fixtures", params={"date": date_yyyy_mm_dd})

    # PUBLIC_INTERFACE
    async def standings(self, league_id: int, season: int) -> Dict[str, Any]:
        """Fetch standings for league/season."""
        return await self._get("standings", params={"league": league_id, "season": season})


client = ApiFootballClient()
