from __future__ import annotations

import asyncio
from typing import Any, Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Manages active websocket connections and broadcast messaging."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast_json(self, message: Dict[str, Any]) -> None:
        async with self._lock:
            conns = list(self._connections)
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)


manager = ConnectionManager()
