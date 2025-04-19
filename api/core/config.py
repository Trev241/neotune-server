from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "Neotune API"
    DATABASE_URL: str
    DEBUG: bool = False
    PORT: int = 5000

    # JWT Settings
    JWT_SECRET: str  # Change in production
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 9999  # minutes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
