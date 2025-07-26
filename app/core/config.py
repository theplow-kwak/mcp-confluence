from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CONFLUENCE_URL: str
    CONFLUENCE_USER: str
    CONFLUENCE_API_TOKEN: str

    # 'gemini', 'openai' 등 사용할 LLM 프로바이더를 선택합니다.
    LLM_PROVIDER: str = "gemini"

    # 각 프로바이더의 API 키 (사용하는 프로바이더의 키만 필요)
    GOOGLE_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
