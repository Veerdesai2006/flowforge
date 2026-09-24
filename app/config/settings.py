"""
=========================================================
FlowForge - Application Settings
=========================================================

WHY THIS FILE EXISTS
--------------------

Instead of reading values from the .env file everywhere
(os.getenv("DB_HOST"), os.getenv("SECRET_KEY"), etc.)

we keep everything inside one Settings class.

Benefits:

✅ Centralized configuration
✅ Type safety
✅ Validation
✅ Auto completion in IDE
✅ Easy to maintain

This file uses Pydantic Settings to automatically load
variables from the .env file.

Example

.env
-----
DB_HOST=localhost

↓

settings.db_host

---------------------------------------------------------
"""

# BaseSettings
# ------------
# Reads values directly from .env and converts them
# into Python variables.
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Every variable here maps to a variable
    inside the .env file.

    Example

    .env

    DB_HOST=localhost

    becomes

    settings.db_host
    """

    # ======================================================
    # Application
    # ======================================================

    app_name: str
    app_version: str
    app_env: str
    debug: bool

    # ======================================================
    # Server
    # ======================================================

    host: str
    port: int

    # ======================================================
    # Database
    # ======================================================

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # ======================================================
    # JWT Authentication
    # ======================================================

    secret_key: str

    # HS256 is the hashing algorithm used
    # to sign JWT tokens.
    algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # ======================================================
    # Uploads
    # ======================================================

    upload_dir: str

    # ======================================================
    # Email
    # ======================================================

    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    mtp_password: Optional[str] = None
    smtp_from: Optional[str] = None

    # ======================================================
    # AI / Gemini
    # ======================================================

    # The API key for Google Gemini AI.
    # Optional because the AI chatbot feature is optional —
    # the rest of the app works fine without it.
    # The value comes from GEMINI_API_KEY in the .env file.
    gemini_api_key: Optional[str] = None

    # ======================================================
    # Pydantic Settings Configuration
    # ======================================================

    model_config = SettingsConfigDict(

        # Name of our environment file.
        env_file=".env",

        # Encoding used while reading .env.
        env_file_encoding="utf-8",

        # Ignore upper/lower case differences.
        case_sensitive=False,

        # Ignore unknown variables present inside .env.
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """
        Build PostgreSQL URL dynamically.

        Instead of writing this inside .env,
        we generate it automatically.

        Output

        postgresql+psycopg2://postgres:password@localhost:5432/flowforge
        """

        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )


"""
Singleton Object
----------------

Only one Settings object will be created
for the entire application.

Anywhere in the project

from app.config.settings import settings

print(settings.db_host)

works without creating multiple objects.
"""

settings = Settings()