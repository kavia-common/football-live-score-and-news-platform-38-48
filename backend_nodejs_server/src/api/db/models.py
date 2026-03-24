from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    api_football_team_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    founded: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    venue_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_teams_name", "name"),)


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    api_football_league_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    season: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("api_football_league_id", "season", name="uq_competitions_api_id_season"),
        Index("idx_competitions_name", "name"),
    )


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    api_football_fixture_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    competition_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("competitions.id"), nullable=True)
    competition: Mapped[Optional[Competition]] = relationship("Competition", lazy="joined")

    season: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    round_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status_short: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    status_long: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status_elapsed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    match_date_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    home_team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    home_team: Mapped[Team] = relationship("Team", foreign_keys=[home_team_id], lazy="joined")
    away_team: Mapped[Team] = relationship("Team", foreign_keys=[away_team_id], lazy="joined")

    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    ht_home: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ht_away: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ft_home: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ft_away: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    venue_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    venue_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_matches_date", "match_date_utc"),
        Index("idx_matches_comp_season", "competition_id", "season"),
        Index("idx_matches_home_team_date", "home_team_id", "match_date_utc"),
        Index("idx_matches_away_team_date", "away_team_id", "match_date_utc"),
    )


class Standing(Base):
    __tablename__ = "standings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    competition_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("competitions.id"), nullable=False)
    competition: Mapped[Competition] = relationship("Competition", lazy="joined")

    season: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    team: Mapped[Team] = relationship("Team", lazy="joined")

    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    played: Mapped[int] = mapped_column(Integer, nullable=False)
    win: Mapped[int] = mapped_column(Integer, nullable=False)
    draw: Mapped[int] = mapped_column(Integer, nullable=False)
    loss: Mapped[int] = mapped_column(Integer, nullable=False)
    goals_for: Mapped[int] = mapped_column(Integer, nullable=False)
    goals_against: Mapped[int] = mapped_column(Integer, nullable=False)
    goal_diff: Mapped[int] = mapped_column(Integer, nullable=False)
    form: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("competition_id", "season", "team_id", name="uq_standings_comp_season_team"),
        Index("idx_standings_comp_season_position", "competition_id", "season", "position"),
    )


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    match: Mapped[Match] = relationship("Match", lazy="joined")

    api_football_event_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    elapsed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    team_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=True)
    team: Mapped[Optional[Team]] = relationship("Team", lazy="joined")

    player_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assist_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    event_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    event_detail: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
