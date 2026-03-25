import os
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environment
    env: str = "dev"

    # App
    project_name: str = "BookDigest API"
    service_name: str = "book-digest-api"
    version: str = "0.1.0"
    api_prefix: str = "/api"
    debug: bool = False

    # Database
    db_driver: str = "postgresql+asyncpg"
    db_user: str = "postgres"
    db_password: SecretStr
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"

    @property
    def db_url(self) -> SecretStr:
        return SecretStr(
            f"{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="allow")


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("ENV", "dev")
    return Settings(env=env, _env_file=f".env.{env}")
