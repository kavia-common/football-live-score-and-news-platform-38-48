from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (bearer)")


class SignupRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    display_name: Optional[str] = Field(None, description="Optional display name")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: int = Field(..., description="User id")
    email: str = Field(..., description="Email")
    display_name: Optional[str] = Field(None, description="Display name")


class TeamOut(BaseModel):
    id: int
    api_football_team_id: Optional[int] = None
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None


class CompetitionOut(BaseModel):
    id: int
    api_football_league_id: Optional[int] = None
    name: str
    country: Optional[str] = None
    season: Optional[int] = None
    logo_url: Optional[str] = None


class MatchOut(BaseModel):
    id: int
    api_football_fixture_id: Optional[int] = None
    competition: Optional[CompetitionOut] = None
    season: Optional[int] = None
    round_name: Optional[str] = None
    status_short: Optional[str] = None
    status_long: Optional[str] = None
    status_elapsed: Optional[int] = None
    match_date_utc: datetime
    timezone: Optional[str] = None
    home_team: TeamOut
    away_team: TeamOut
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    ht_home: Optional[int] = None
    ht_away: Optional[int] = None
    ft_home: Optional[int] = None
    ft_away: Optional[int] = None
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None


class StandingOut(BaseModel):
    competition: CompetitionOut
    season: int
    team: TeamOut
    position: int
    points: int
    played: int
    win: int
    draw: int
    loss: int
    goals_for: int
    goals_against: int
    goal_diff: int
    form: Optional[str] = None
    updated_at: datetime


class NewsArticleOut(BaseModel):
    source: Optional[str] = None
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: Optional[str] = None
    content: Optional[str] = None


class NewsResponse(BaseModel):
    status: str = Field(..., description="NewsAPI status")
    totalResults: int = Field(..., description="Total articles")
    articles: List[NewsArticleOut] = Field(default_factory=list)


class WSMatchUpdate(BaseModel):
    """WebSocket payload used for match updates."""
    type: str = Field("match_update", description="Message type")
    fixture_id: Optional[int] = Field(None, description="API-Football fixture id, when available")
    match: Optional[Dict[str, Any]] = Field(None, description="Match object (compact)")
