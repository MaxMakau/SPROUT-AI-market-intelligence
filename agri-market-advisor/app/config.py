"""
Configuration module for Agri-Market Advisor system.
Loads environment variables and provides settings using Pydantic.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = "Sprout AI - Agri-Market Advisor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # External APIs
    google_maps_api_key: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # USSD Configuration
    ussd_short_code: str = "*384*88888#"
    
    # SMS Configuration
    sms_provider: str = "AfriksTalk"  # Mock provider
    
    # WhatsApp Configuration
    whatsapp_api_url: Optional[str] = os.getenv("WHATSAPP_API_URL")
    
    # ML Model Configuration
    model_path: str = "app/models/market_model.pkl"
    scaler_path: str = "app/models/scaler.pkl"
    
    # Data Configuration
    csv_data_path: str = "data/wfp_food_prices_ken.csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Initialize settings
settings = Settings()
