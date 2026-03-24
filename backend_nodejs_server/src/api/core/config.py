import os
from dataclasses import dataclass
from typing import List, Optional


def _parse_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    # Core
    env: str
    host: str
    port: int
    trust_proxy: bool

    # CORS
    allowed_origins: List[str]
    allowed_headers: List[str]
    allowed_methods: List[str]
    cors_max_age: int

    # Auth / JWT
    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    jwt_access_token_ttl_s: int

    # Rate limiting (simple in-memory)
    rate_limit_window_s: int
    rate_limit_max: int

    # MySQL
    mysql_url: Optional[str]
    mysql_user: Optional[str]
    mysql_password: Optional[str]
    mysql_db: Optional[str]
    mysql_port: Optional[str]

    # External API keys
    api_football_key: Optional[str]
    api_football_host: str
    newsapi_key: Optional[str]

    # Caching
    cache_ttl_s: int

    # Realtime polling
    live_poll_interval_s: int

    @staticmethod
    def load() -> "Settings":
        # NOTE: Environment variables are expected to be provided via .env by orchestrator.
        env = os.getenv("NODE_ENV", "development")

        host = os.getenv("UVICORN_HOST", os.getenv("HOST", "0.0.0.0"))
        port = int(os.getenv("PORT", "3001"))
        trust_proxy = os.getenv("TRUST_PROXY", "false").lower() == "true"

        allowed_origins = _parse_csv(os.getenv("ALLOWED_ORIGINS", "*"))
        if not allowed_origins:
            allowed_origins = ["*"]

        allowed_headers = _parse_csv(os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization"))
        allowed_methods = _parse_csv(os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS"))
        cors_max_age = int(os.getenv("CORS_MAX_AGE", "3600"))

        jwt_secret = os.getenv("JWT_SECRET", "")
        jwt_issuer = os.getenv("JWT_ISSUER", "football-live-scores-backend")
        jwt_audience = os.getenv("JWT_AUDIENCE", "football-live-scores-mobile")
        jwt_access_token_ttl_s = int(os.getenv("JWT_ACCESS_TOKEN_TTL_S", "86400"))

        rate_limit_window_s = int(os.getenv("RATE_LIMIT_WINDOW_S", "60"))
        rate_limit_max = int(os.getenv("RATE_LIMIT_MAX", "100"))

        mysql_url = os.getenv("MYSQL_URL")
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_db = os.getenv("MYSQL_DB")
        mysql_port = os.getenv("MYSQL_PORT")

        api_football_key = os.getenv("API_FOOTBALL_KEY")
        api_football_host = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")
        newsapi_key = os.getenv("NEWSAPI_KEY")

        cache_ttl_s = int(os.getenv("CACHE_TTL_S", "30"))
        live_poll_interval_s = int(os.getenv("LIVE_POLL_INTERVAL_S", "15"))

        return Settings(
            env=env,
            host=host,
            port=port,
            trust_proxy=trust_proxy,
            allowed_origins=allowed_origins,
            allowed_headers=allowed_headers,
            allowed_methods=allowed_methods,
            cors_max_age=cors_max_age,
            jwt_secret=jwt_secret,
            jwt_issuer=jwt_issuer,
            jwt_audience=jwt_audience,
            jwt_access_token_ttl_s=jwt_access_token_ttl_s,
            rate_limit_window_s=rate_limit_window_s,
            rate_limit_max=rate_limit_max,
            mysql_url=mysql_url,
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            mysql_db=mysql_db,
            mysql_port=mysql_port,
            api_football_key=api_football_key,
            api_football_host=api_football_host,
            newsapi_key=newsapi_key,
            cache_ttl_s=cache_ttl_s,
            live_poll_interval_s=live_poll_interval_s,
        )


settings = Settings.load()
