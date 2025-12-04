"""
Market forecast service using ML model.
Predicts market prices for different locations.
"""

from typing import Dict, List
from app.models import MarketPricePredictor
from app.utils.constants import MARKET_LOCATIONS


class MarketForecastService:
    """
    Service for forecasting market prices using ML model.
    """
    
    def __init__(self):
        """Initialize the forecast service with ML model."""
        self.model = MarketPricePredictor()
        self.market_locations = MARKET_LOCATIONS
    
    def forecast_all_markets(self,
                            produce: str,
                            quantity: float,
                            location: str,
                            transport_mode: str,
                            has_storage: bool) -> Dict[str, float]:
        """
        Forecast prices across all market locations.
        
        Args:
            produce: Type of produce
            quantity: Quantity in kg
            location: Farmer's location
            transport_mode: Transport mode
            has_storage: Whether farmer has storage
            
        Returns:
            Dictionary mapping markets to predicted prices
        """
        forecasts = {}
        
        for market in self.market_locations:
            price = self.model.predict(
                produce=produce,
                quantity=quantity,
                location=location,
                transport_mode=transport_mode,
                has_storage=has_storage,
                market=market
            )
            forecasts[market] = price
        
        return forecasts
    
    def forecast_specific_market(self,
                                produce: str,
                                quantity: float,
                                location: str,
                                transport_mode: str,
                                has_storage: bool,
                                market: str) -> float:
        """
        Forecast price for a specific market.
        
        Args:
            produce: Type of produce
            quantity: Quantity in kg
            location: Farmer's location
            transport_mode: Transport mode
            has_storage: Whether farmer has storage
            market: Target market
            
        Returns:
            Predicted price
        """
        return self.model.predict(
            produce=produce,
            quantity=quantity,
            location=location,
            transport_mode=transport_mode,
            has_storage=has_storage,
            market=market
        )
    
    def get_market_trends(self, produce: str, market: str) -> dict:
        """
        Get market trend information (mock implementation).
        
        Args:
            produce: Type of produce
            market: Market location
            
        Returns:
            Dictionary with trend information
        """
        return {
            "produce": produce,
            "market": market,
            "trend": "stable",
            "forecast_7days": "neutral",
            "demand": "steady",
            "supply": "adequate"
        }
    
    def get_seasonal_adjustment(self, produce: str, month: int) -> float:
        """
        Get seasonal price adjustment for produce.
        
        Args:
            produce: Type of produce
            month: Month number (1-12)
            
        Returns:
            Seasonal adjustment factor
        """
        # Mock seasonal data
        seasonal_patterns = {
            "maize": [1.0, 0.95, 0.90, 0.85, 0.80, 0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.05],
            "tomato": [1.2, 1.15, 1.1, 0.9, 0.85, 0.80, 0.85, 0.90, 0.95, 1.05, 1.15, 1.20],
            "onion": [0.9, 0.95, 1.0, 1.05, 1.10, 1.05, 1.0, 0.95, 0.90, 0.85, 0.85, 0.90],
        }
        
        pattern = seasonal_patterns.get(produce.lower(), [1.0] * 12)
        return pattern[month - 1] if 1 <= month <= 12 else 1.0
    
    def compare_markets(self,
                       produce: str,
                       quantity: float,
                       location: str,
                       transport_mode: str,
                       has_storage: bool) -> List[dict]:
        """
        Compare forecasts across markets and rank them.
        
        Args:
            produce: Type of produce
            quantity: Quantity in kg
            location: Farmer's location
            transport_mode: Transport mode
            has_storage: Whether farmer has storage
            
        Returns:
            List of markets ranked by predicted price (descending)
        """
        forecasts = self.forecast_all_markets(
            produce, quantity, location, transport_mode, has_storage
        )
        
        # Sort by price (descending)
        ranked = sorted(
            [{"market": m, "predicted_price": p} for m, p in forecasts.items()],
            key=lambda x: x["predicted_price"],
            reverse=True
        )
        
        for i, item in enumerate(ranked, 1):
            item["rank"] = i
        
        return ranked
