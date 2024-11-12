from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    MONGO_URL: str
    REDIS_URL: str


class APISettings(BaseSettings):
    OSU_CLIENT_ID: str
    OSU_CLIENT_SECRET: str
    OSU_REDIRECT_URI: str
    POST_LOGIN_REDIRECT_URI: str


class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"


class SentrySettings(BaseSettings):
    SENTRY_DSN: str


class TestSettings(BaseSettings):
    TEST_USER_ID: str


class Settings(
    DatabaseSettings, APISettings, AuthSettings, SentrySettings, TestSettings
):
    pass


settings = Settings()
