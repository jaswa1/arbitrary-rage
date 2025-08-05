"""
Application configuration settings using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Arbitrage Detection System"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/arbitrage_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "change-this-super-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080",
    ]
    
    # Scraping Configuration
    SCRAPING_DELAY_MS: int = 2000  # Delay between requests in milliseconds
    MAX_CONCURRENT_REQUESTS: int = 10
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Alert Configuration
    SLACK_WEBHOOK_URL: Optional[str] = None
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: int = 587
    EMAIL_USER: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    
    # Business Logic Thresholds
    MIN_MARGIN_THRESHOLD: float = 25.0  # Minimum margin percentage to flag opportunities
    MAX_RISK_LEVEL: str = "medium"  # Maximum risk level for auto-alerts
    DEFAULT_PRICE_FLOOR: float = 0.35  # Default minimum price for singles
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Feature Flags
    ENABLE_SCRAPING: bool = True
    ENABLE_ALERTS: bool = True
    ENABLE_AUTO_EXECUTION: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()