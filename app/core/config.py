from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Travel Planner API"

    DATABASE_URL: str = "sqlite+aiosqlite:///./travel_planner.db"

    DB_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
