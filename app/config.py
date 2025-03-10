from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str
    DATABASE_NAME: str

    # JWT settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:5173"]
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_OAUTH_REDIRECT_URI: str
    AGENT_EMAIL_ADDRESS: str
    GOOGLE_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

        # Add aliases for environment variables if needed
        alias_generator = lambda x: x.upper()  # This will look for uppercase env variables

settings = Settings()

# Print debug info on startup
print("Settings loaded:")
print(f"JWT_SECRET: {settings.JWT_SECRET[:5]}...")
print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}") 