from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    nova_lite_model_id: str = "us.amazon.nova-lite-v1:0"
    nova_sonic_model_id: str = "amazon.nova-sonic-v1:0"
    csv_path: str = "backend/data/homes.csv"
    max_results: int = 10
    session_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
