from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    MONGODB_URL: str


class APISettings(BaseSettings):
    OSU_CLIENT_ID: str
    OSU_CLIENT_SECRET: str
    OSU_REDIRECT_URI: str


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"


class Settings(
    DatabaseSettings, APISettings, AuthSettings
):
    pass


settings = Settings()
