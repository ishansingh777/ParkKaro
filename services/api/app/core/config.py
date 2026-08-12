from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@db:5432/parkkaro"
    JWT_SECRET: str = "your_jwt_secret_here"
    
    class Config:
        env_file = "../../.env"

settings = Settings()
