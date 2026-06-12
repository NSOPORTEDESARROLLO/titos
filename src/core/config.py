"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_token: str
    app_name: str = "Titos API"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 5001
    otobo_ip: str = ""
    otobo_user: str = ""
    otobo_pwd: str = ""
    webhook_tester: str = ""
    otobo_timeout: int = 30
    otobo_verify_ssl: bool = True
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
