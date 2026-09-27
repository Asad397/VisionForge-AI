from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = 'VisionForge AI'
    app_env: str = 'development'
    secret_key: str = 'change-me'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1440
    database_url: str = 'postgresql://visionforge:visionforge@localhost:5432/visionforge'
    redis_url: str = 'redis://localhost:6379/0'
    frontend_url: str = 'http://localhost:3000'
    backend_url: str = 'http://localhost:8000'
    ai_mock_mode: bool = True
    ai_device: str = 'cpu'
    admin_email: str = 'admin@visionforge.ai'
    admin_password: str = 'admin123'
    rate_limit_per_minute: int = 60

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


@lru_cache()
def get_settings() -> Settings:
    return Settings()
