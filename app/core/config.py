from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CONFLUENCE_URL: str
    CONFLUENCE_USER: str
    CONFLUENCE_API_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

