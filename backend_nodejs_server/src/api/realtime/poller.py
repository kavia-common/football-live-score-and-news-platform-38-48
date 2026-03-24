from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from src.api.core.config import settings
from src.api.integrations.api_football import client as api_football
from src.api.realtime.ws_manager import manager


def _compact_fixture(fixture_item: Dict[str, Any]) -> Dict[str, Any]:
    fixture = fixture_item.get("fixture", {})
    teams = fixture_item.get("teams", {})
    goals = fixture_item.get("goals", {})
    league = fixture_item.get("league", {})
    status = fixture.get("status", {})

    return {
        "fixture_id": fixture.get("id"),
        "date": fixture.get("date"),
        "league": {
            "id": league.get("id"),
            "name": league.get("name"),
            "country": league.get("country"),
            "season": league.get("season"),
            "round": league.get("round"),
        },
        "status": {
            "short": status.get("short"),
            "long": status.get("long"),
            "elapsed": status.get("elapsed"),
        },
        "teams": {
            "home": {"id": teams.get("home", {}).get("id"), "name": teams.get("home", {}).get("name")},
            "away": {"id": teams.get("away", {}).get("id"), "name": teams.get("away", {}).get("name")},
        },
        "goals": {"home": goals.get("home"), "away": goals.get("away")},
    }


class LiveMatchPoller:
    """Polls API-Football live fixtures and broadcasts updates to websocket clients."""

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except Exception:
                self._task.cancel()

    async def _run(self) -> None:
        # Best-effort loop: never crash the server due to upstream errors.
        while not self._stop.is_set():
            try:
                data = await api_football.fixtures_live()
                response = data.get("response") or []
                for item in response:
                    payload = {
                        "type": "match_update",
                        "fixture_id": item.get("fixture", {}).get("id"),
                        "match": _compact_fixture(item),
                    }
                    await manager.broadcast_json(payload)
            except Exception:
                # swallow errors; polling resumes next tick
                pass

            try:
                await asyncio.wait_for(self._stop.wait(), timeout=settings.live_poll_interval_s)
            except asyncio.TimeoutError:
                continue


poller = LiveMatchPoller()
