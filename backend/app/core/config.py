# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    mongo_url: str   # ✅ BU ÇOK ÖNEMLİ
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        extra = "allow"   # ✅ Fazla env değişkenine izin ver

settings = Settings()

