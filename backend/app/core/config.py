from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Knowledge Search"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]

    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_INDEX: str = "documents"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "knowledge"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    MAX_UPLOAD_SIZE_MB: int = 20
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()