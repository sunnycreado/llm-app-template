from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    port: int = 4000
    log_level: str = "info"

    # NVIDIA NIM
    nim_api_key: str
    nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nim_model: str = "meta/llama-3.1-8b-instruct"
    nim_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    nim_rerank_model: str = "nvidia/llama-3.2-nv-rerankqa-1b-v2"
    nim_timeout_ms: int = 30000

    # Prompts
    prompt_name: str = "base"
    prompt_version: str = "latest"

    # Vector store
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"

    # PostgreSQL
    postgres_user: str = "appuser"
    postgres_password: str = "apppassword"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "appdb"

    # Memory
    redis_url: str = "redis://localhost:6379"
    use_redis: bool = False

    # LangGraph
    langgraph_recursion_limit: int = 25

    @property
    def nim_timeout(self) -> float:
        return self.nim_timeout_ms / 1000

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
