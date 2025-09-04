from pydantic_settings import BaseSettings, SettingsConfigDict


_base_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = _base_config

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class SecuritySettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    model_config = _base_config


class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str

    model_config = _base_config

class llmSettings(BaseSettings):
    GEMINI_API_KEY: str
    LANGSMITH_API_KEY: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_PROJECT: str
    LANGSMITH_TRACING: str

    model_config = _base_config

db_settings = DatabaseSettings()
security_settings = SecuritySettings()
aws_settings = AWSSettings()
llm_settings = llmSettings()