import os
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret")
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
    PASSWORD_FILE = Path(os.environ.get("PASSWORD_FILE") or BASE_DIR / ".admin_password")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    CONTENT_DIR = Path(os.environ.get("CONTENT_DIR") or BASE_DIR / "content")
    REPO_DIR = Path(os.environ.get("REPO_DIR") or BASE_DIR)
    RUN_DEPLOY = os.environ.get("RUN_DEPLOY") == "1"
    POSTS_PER_PAGE = 10
    SITE_NAME = "HONGS"
    SITE_LAUNCH_DATE = date(2026, 8, 26)
