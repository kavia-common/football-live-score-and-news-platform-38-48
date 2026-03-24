from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.auth.deps import get_current_user
from src.api.auth.security import create_access_token, hash_password, verify_password
from src.api.db.models import User
from src.api.db.session import get_db
from src.api.integrations.api_football import client as api_football
from src.api.integrations.newsapi import client as newsapi
from src.api.schemas import LoginRequest, NewsResponse, SignupRequest, TokenResponse, UserResponse

router = APIRouter()

auth_router = APIRouter(prefix="/auth", tags=["auth"])
football_router = APIRouter(prefix="/football", tags=["football"])
news_router = APIRouter(prefix="/news", tags=["news"])
users_router = APIRouter(prefix="/users", tags=["users"])


@auth_router.post(
    "/signup",
    response_model=TokenResponse,
    summary="Create a new user account",
    description="Creates a new account and returns a JWT access token.",
    operation_id="auth_signup",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # Check existing
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Returns a JWT access token if credentials are valid.",
    operation_id="auth_login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@users_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the currently authenticated user's basic profile.",
    operation_id="users_me",
)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=current_user.id, email=current_user.email, display_name=current_user.display_name)


@football_router.get(
    "/live",
    summary="Get live football fixtures/scores",
    description="Fetches live fixtures from API-Football (cached).",
    operation_id="football_live",
)
async def live_scores() -> Dict[str, Any]:
    return await api_football.fixtures_live()


@football_router.get(
    "/fixtures",
    summary="Get fixtures by date (schedule)",
    description="Fetches fixtures for a date (YYYY-MM-DD) from API-Football (cached).",
    operation_id="football_fixtures_by_date",
)
async def fixtures_by_date(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
) -> Dict[str, Any]:
    return await api_football.fixtures_by_date(date_yyyy_mm_dd=date)


@football_router.get(
    "/standings",
    summary="Get league standings",
    description="Fetches standings for league_id and season from API-Football (cached).",
    operation_id="football_standings",
)
async def standings(
    league_id: int = Query(..., description="API-Football league id"),
    season: int = Query(..., description="Season year (e.g. 2024)"),
) -> Dict[str, Any]:
    return await api_football.standings(league_id=league_id, season=season)


@news_router.get(
    "",
    response_model=NewsResponse,
    summary="Get latest football news",
    description="Fetches football headlines from NewsAPI (cached).",
    operation_id="news_latest",
)
async def latest_news(
    q: str = Query("football", description="Search query"),
    page_size: int = Query(20, ge=1, le=100, description="Number of articles to return"),
) -> Dict[str, Any]:
    return await newsapi.top_headlines(query=q, page_size=page_size)


router.include_router(auth_router)
router.include_router(users_router)
router.include_router(football_router)
router.include_router(news_router)
