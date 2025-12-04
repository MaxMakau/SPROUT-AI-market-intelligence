"""
External API integration module.
Handles calls to Google Maps API and other external services.
"""

from typing import Optional, Dict
import random


class ExternalAPIService:
    """
    Service for handling external API calls.
    Includes mock implementations for demo purposes.
    """
    
    def __init__(self, google_maps_key: Optional[str] = None):
        """Initialize external API service."""
        self.google_maps_key = google_maps_key
    
    def get_distance_google_maps(self,
                                origin: str,
                                destination: str) -> Optional[float]:
        """
        Get distance between two locations using Google Maps API.
        Mock implementation - returns simulated distance.
        
        Args:
            origin: Starting location
            destination: Destination location
            
        Returns:
            Distance in kilometers or None if error
        """
        if not self.google_maps_key:
            return self._mock_distance(origin, destination)
        
        # In production, make actual API call
        try:
            return self._mock_distance(origin, destination)
        except Exception as e:
            print(f"Error calling Google Maps API: {e}")
            return self._mock_distance(origin, destination)
    
    def _mock_distance(self, origin: str, destination: str) -> float:
        """
        Generate mock distance data for testing.
        
        Args:
            origin: Starting location
            destination: Destination location
            
        Returns:
            Mock distance in kilometers
        """
        # Mock distance matrix
        distances = {
            ("Nairobi", "Kiambu"): 25,
            ("Nairobi", "Muranga"): 50,
            ("Nairobi", "Mombasa"): 480,
            ("Nairobi", "Kisumu"): 400,
            ("Nairobi", "Nakuru"): 160,
            ("Nairobi", "Kericho"): 220,
            ("Kiambu", "Muranga"): 40,
        }
        
        key = tuple(sorted([origin, destination]))
        return distances.get(key, random.randint(50, 300))
    
    def get_weather_forecast(self, location: str, days: int = 7) -> dict:
        """
        Get weather forecast for location.
        Mock implementation.
        
        Args:
            location: Location name
            days: Number of days to forecast
            
        Returns:
            Dictionary with weather data
        """
        return {
            "location": location,
            "forecast_days": days,
            "temperature_avg": 22,
            "humidity_avg": 70,
            "rainfall_probability": 0.3,
            "status": "stable"
        }
    
    def get_market_trends(self, produce: str, market: str) -> dict:
        """
        Get market trend data using external API.
        Mock implementation.
        
        Args:
            produce: Type of produce
            market: Market location
            
        Returns:
            Dictionary with trend data
        """
        trends = {
            "produce": produce,
            "market": market,
            "price_trend": random.choice(["up", "stable", "down"]),
            "demand_level": random.choice(["high", "medium", "low"]),
            "supply_level": random.choice(["high", "medium", "low"]),
            "forecast_7days": random.choice(["bullish", "neutral", "bearish"])
        }
        return trends
    
    def get_currency_exchange_rate(self,
                                  from_currency: str = "KES",
                                  to_currency: str = "USD") -> Optional[float]:
        """
        Get current exchange rate.
        Mock implementation.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate or None if error
        """
        # Mock exchange rates
        rates = {
            ("KES", "USD"): 0.0077,
            ("KES", "EUR"): 0.0071,
            ("USD", "KES"): 129.87,
            ("EUR", "KES"): 140.85,
        }
        
        key = (from_currency.upper(), to_currency.upper())
        return rates.get(key, None)
    
    def send_sms_notification(self,
                             phone_number: str,
                             message: str) -> dict:
        """
        Send SMS notification (mock implementation).
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            
        Returns:
            Dictionary with send status
        """
        return {
            "status": "success",
            "phone_number": phone_number,
            "message": message,
            "timestamp": "2024-12-03T10:30:00Z"
        }
    
    def send_whatsapp_message(self,
                             phone_number: str,
                             message: str) -> dict:
        """
        Send WhatsApp message (mock implementation).
        
        Args:
            phone_number: Recipient phone number
            message: Message content
            
        Returns:
            Dictionary with send status
        """
        return {
            "status": "success",
            "platform": "whatsapp",
            "phone_number": phone_number,
            "message": message,
            "timestamp": "2024-12-03T10:30:00Z"
        }
    
    def get_ai_market_summary(self, market_data: dict) -> str:
        """
        Get AI-generated market summary (mock implementation).
        In production, could use GPT/Gemini API.
        
        Args:
            market_data: Dictionary with market information
            
        Returns:
            AI-generated summary text
        """
        produce = market_data.get("produce", "produce")
        market = market_data.get("market", "market")
        profit = market_data.get("net_profit", 0)
        
        return (
            f"Based on current market conditions, {produce} is performing well in {market}. "
            f"Expected profit is KES {profit:,.0f}. "
            f"Market demand is steady with stable prices. Recommend transporting immediately to capture current prices."
        )
