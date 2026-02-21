from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    ENVIRONMENT: str = "docker"

    API_V1_PREFIX: str = "/api/v1"

    REFRESH_TOKEN_DAYS: int = 7
    ACCESS_KEY_TIMEDELTA_MINUTES: int = 60

    SECRET_KEY_ACCESS: str = Field(
        "placeholder_access", alias="SECRET_KEY_ACCESS"
    )
    SECRET_KEY_REFRESH: str = Field(
        "placeholder_refresh", alias="SECRET_KEY_REFRESH"
    )
    JWT_SIGNING_ALGORITHM: str = "HS256"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB_PORT: int = 5432
    POSTGRES_DB: str

    ART_INSTITUTE_API_URL: str = Field(
        "placeholder_url", alias="ART_INSTITUTE_API_URL"
    )

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}"
            f":{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}"
            f":{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB}"
        )
