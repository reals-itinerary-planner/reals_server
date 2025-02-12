from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
import os


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # Application
    PROJECT_NAME: str = "Reals API"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    # Database Pool Settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 60
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO_LOG: bool = False

    # Migration Settings
    MIGRATIONS_DIR: str = "migrations"
    ALEMBIC_CONFIG: str = "alembic.ini"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GPT_API_URL: str = "https://api.openai.com/v1/chat/completions"
    ORGANIZATION_ID: str | None = None
    PROJECT_ID: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        """Get database URL based on environment"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Get synchronous database URL for migrations"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        use_enum_values = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            env = os.getenv("ENVIRONMENT", "development")
            env_file = f".env.{env}"
            if os.path.exists(env_file):
                cls.env_file = env_file

            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
