from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FMS Platform API"
    app_version: str = "0.1.0"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://fms:fms_password@localhost:5432/fms"
    storage_provider: str = "local"
    storage_bucket: str = "fms-local-documents"
    local_storage_root: str = "storage/documents"
    max_upload_size_bytes: int = 50_000_000
    fop_upload_root: str | None = Field(default=None, alias="FOP_UPLOAD_ROOT")
    fop_max_upload_mb: int | None = Field(default=None, alias="FOP_MAX_UPLOAD_MB")
    fop_allowed_upload_types_raw: str = Field(
        default="application/pdf,text/plain,text/csv,image/png,image/jpeg",
        alias="FOP_ALLOWED_UPLOAD_TYPES",
    )
    backend_cors_origins_raw: str = Field(
        default="http://localhost:3000",
        alias="BACKEND_CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def backend_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins_raw.split(",")
            if origin.strip()
        ]

    @property
    def upload_root(self) -> str:
        return self.fop_upload_root or self.local_storage_root

    @property
    def upload_max_size_bytes(self) -> int:
        if self.fop_max_upload_mb is not None:
            return self.fop_max_upload_mb * 1024 * 1024
        return self.max_upload_size_bytes

    @property
    def allowed_upload_types(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.fop_allowed_upload_types_raw.split(",")
            if item.strip()
        }


settings = Settings()
