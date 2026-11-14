import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    # MongoDB Config
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "trust_sell")

    # Security Settings
    # Fallback to a development key, warn if in production (defaulting to secure setup)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-do-not-use-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

    # Server Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENV: str = os.getenv("ENV", "development")
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "").lower() in ("1", "true", "yes")

    # Storage Settings for Verification Files
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Secure absolute path for file storage
    @property
    def UPLOAD_PATH(self) -> Path:
        path = BASE_DIR / self.UPLOAD_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = Settings()
