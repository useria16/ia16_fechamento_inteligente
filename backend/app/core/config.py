from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_ENV: str = "dev"
    DB_SCHEMA: str = "ia16_fechamento_dev"
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    STORAGE_ENV_PREFIX: str = "dev"
    SECRET_KEY: str = "change_me"


settings = Settings()
