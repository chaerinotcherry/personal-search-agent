from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_auth_token: str = "psa-local-token"
    embedding_model: str = "jhgan/ko-sroberta-multitask"
    local_folder_path: str = "/data/local"
    collection_name: str = "documents"
    chunk_size: int = 512
    chunk_overlap: int = 64
    openai_api_key: str = ""
    groq_api_key: str = ""
    notion_api_key: str = ""
    gdrive_credentials_path: str = "/app/gdrive_creds/credentials.json"
    gdrive_token_path: str = "/app/gdrive_creds/token.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = AppSettings()
