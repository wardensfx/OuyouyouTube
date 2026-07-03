"""
Configuration centralisée, lue depuis les variables d'environnement (.env).
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    # Session / JWT
    secret_key: str = "change-me-in-prod"
    session_cookie_name: str = "ytpwa_session"

    # Stockage / cache vidéo
    cache_dir: Path = Path("/tmp/ytpwa_cache")
    video_ttl_seconds: int = 60 * 30  # 30 min avant suppression auto
    cleanup_interval_seconds: int = 60 * 5  # fréquence du job de nettoyage

    # Redis (cache métadonnées YouTube)
    redis_url: str = "redis://localhost:6379/0"
    metadata_ttl_seconds: int = 60 * 15

    # Frontend (CORS)
    frontend_origin: str = "http://localhost:5173"

    # yt-dlp
    ytdlp_cookies_file: str | None = None  # chemin vers cookies.txt export navigateur

    class Config:
        env_file = ".env"


settings = Settings()
settings.cache_dir.mkdir(parents=True, exist_ok=True)
