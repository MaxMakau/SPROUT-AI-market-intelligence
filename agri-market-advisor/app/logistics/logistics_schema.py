"""
Pydantic schemas for logistics request and response validation.
"""

from pydantic import BaseModel, Field


class LogisticsRequest(BaseModel):
    """Request schema for logistics recommendation."""
    
    quantity_sacks: int = Field(..., gt=0, description="Number of sacks to transport")
    distance_km: float = Field(..., ge=0, description="Distance to market in kilometers")
    best_market_location: str = Field(..., description="Name of the best market location")
    market_price: float = Field(..., gt=0, description="Expected market price in KES")
    
    class Config:
        schema_extra = {
            "example": {
                "quantity_sacks": 5,
                "distance_km": 85.5,
                "best_market_location": "Nairobi Central Market",
                "market_price": 2500.0
            }
        }


class LogisticsResponse(BaseModel):
    """Response schema for logistics recommendation."""
    
    transport_mode: str = Field(..., description="Recommended transport mode (motorbike, pickup, or lorry)")
    transport_cost_kes: int = Field(..., description="Total transport cost in KES")
    distance_km: float = Field(..., description="Distance to market in kilometers")
    best_market_location: str = Field(..., description="Best market location")
    market_price: float = Field(..., description="Market price in KES")
    
    class Config:
        schema_extra = {
            "example": {
                "transport_mode": "pickup",
                "transport_cost_kes": 3500,
                "distance_km": 85.5,
                "best_market_location": "Nairobi Central Market",
                "market_price": 2500.0
            }
        }
