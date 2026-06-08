from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WM 2026 Predictor API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./wm2026.db"
    cors_origins: list[str] = ["https://wm.wentzek-home.de", "http://localhost:6238"]
    football_data_api_key: str | None = None
    football_data_base_url: str = "https://api.football-data.org"
    model_artifact_path: str = "models_artifacts/match_outcome_model.joblib"
    historical_matches_csv: str = "../data/historical/results.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
