from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import settings
from src.api.db.init_db import db_ping, init_db
from src.api.realtime.poller import poller
from src.api.realtime.ws_manager import manager
from src.api.routes import router as api_router

openapi_tags = [
    {"name": "auth", "description": "Signup/login and JWT token issuance."},
    {"name": "users", "description": "User profile endpoints."},
    {"name": "football", "description": "Live scores, fixtures, schedules, standings (API-Football)."},
    {"name": "news", "description": "Latest football news (NewsAPI)."},
    {"name": "realtime", "description": "WebSocket for real-time match updates."},
    {"name": "meta", "description": "Health and documentation helpers."},
]

app = FastAPI(
    title="Football Live Scores & News API",
    description=(
        "Backend for a Cricbuzz-like football app: JWT auth, live scores, schedules, standings, and news.\n\n"
        "Realtime: connect to the WebSocket endpoint at `/ws` to receive `match_update` messages."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if settings.allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=settings.allowed_methods or ["*"],
    allow_headers=settings.allowed_headers or ["*"],
    max_age=settings.cors_max_age,
)

app.include_router(api_router)


@app.on_event("startup")
async def _startup() -> None:
    init_db()
    await poller.start()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await poller.stop()


@app.get(
    "/",
    tags=["meta"],
    summary="Health check",
    description="Basic health check plus DB reachability status.",
    operation_id="health_check",
)
def health_check():
    return {"message": "Healthy", "db_ok": db_ping()}


@app.get(
    "/docs/websocket",
    tags=["meta"],
    summary="WebSocket usage help",
    description="Explains how to connect to the WebSocket endpoint and message format.",
    operation_id="websocket_docs",
)
def websocket_docs():
    return {
        "websocket_url": "/ws",
        "message_types": [
            {
                "type": "match_update",
                "description": "Broadcast periodically from background poller while live matches exist.",
            }
        ],
        "notes": [
            "Clients should reconnect on disconnect.",
            "This server polls API-Football on a fixed interval (LIVE_POLL_INTERVAL_S).",
        ],
    }


@app.websocket(
    "/ws",
)
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time match updates.

    Usage:
    - Connect to ws(s)://<host>/ws
    - The server will periodically push JSON messages of the form:
        { "type": "match_update", "fixture_id": <int>, "match": {...} }
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive; accept client pings/messages but ignore content.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)
