"""
Configuration module for Agri-Market Advisor system.
Loads environment variables and provides settings using Pydantic.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
    google_maps_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouteservice_api_key: Optional[str] = None
    ors_api_key: Optional[str] = None
    
    # USSD Configuration
    ussd_short_code: str = "*384*88888#"
    
    # SMS Configuration
    sms_provider: str = "AfriksTalk"  # Mock provider
    
    # WhatsApp Configuration
    whatsapp_api_url: Optional[str] = None
    
    # ML Model Configuration
    model_path: str = "app/models/market_model.pkl"
    scaler_path: str = "app/models/scaler.pkl"
    
    # Data Configuration
    csv_data_path: str = "data/wfp_food_prices_ken.csv"
    # Persistence for prediction jobs (SQLite file path)
    prediction_db_path: str = "data/predictions.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Initialize settings
settings = Settings()
