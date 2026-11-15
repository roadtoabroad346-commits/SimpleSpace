from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"
    irsa_tap_url: str = "https://irsa.ipac.caltech.edu/TAP"
    irsa_obscore_table: str = "ivoa.obscore"
    irsa_query_timeout_seconds: float = 45.0
    irsa_max_rows: int = 100
    spherex_collections: str = "spherex_dr1,spherex_qr2,spherex_qr3"

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def collection_names(self) -> list[str]:
        return [item.strip() for item in self.spherex_collections.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
