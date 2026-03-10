from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
    env_file="./.env",
    env_ignore_empty=True,
    extra="ignore",
)


class DatabaseSettings(BaseSettings):

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str


    REDIS_HOST: str
    REDIS_PORT: int

    model_config = _base_config


    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URL_SYNC(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


    def REDIS_URL(self, db):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"
    


class AppSettings(BaseSettings):
    APP_NAME: str = "Code cards API"
    APP_DOMAIN: str = "localhost:8000"

class AISettings(BaseSettings):
    ANTHROPIC_API_KEY: str

    model_config = _base_config


class SecuritySettings(BaseSettings):

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    model_config = _base_config





db_settings = DatabaseSettings()




ai_settings = AISettings()

security_settings = SecuritySettings()

app_settings = AppSettings()

