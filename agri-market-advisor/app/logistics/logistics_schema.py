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


class DetailedLogisticsResponse(BaseModel):
    """Detailed logistics response with cost breakdown."""
    
    produce: str = Field(..., description="Type of produce")
    quantity_kg: float = Field(..., description="Original quantity in kilograms")
    quantity_sacks: float = Field(..., description="Quantity converted to sacks (1 sack = 90 kg)")
    location: str = Field(..., description="Origin location")
    best_market: str = Field(..., description="Best market destination")
    distance_km: float = Field(..., description="Distance to market in kilometers")
    
    transport_mode: str = Field(..., description="Recommended transport mode (motorbike, pickup, or lorry)")
    cost_per_sack: int = Field(..., description="Cost per sack in KES (varies by transport mode)")
    cost_per_km: int = Field(..., description="Cost per kilometer in KES")
    
    base_cost: int = Field(..., description="Cost based on quantity (quantity_sacks * cost_per_sack) in KES")
    distance_cost: float = Field(..., description="Cost based on distance (distance_km * cost_per_km) in KES")
    total_transport_cost: float = Field(..., description="Total transport cost (base_cost + distance_cost) in KES")
    
    note: str = Field(default="Detailed logistics calculation with kg to sacks conversion", description="Additional note")
    
    class Config:
        schema_extra = {
            "example": {
                "produce": "maize",
                "quantity_kg": 100.0,
                "quantity_sacks": 1.11,
                "location": "Eldoret",
                "best_market": "Eldoret Market",
                "distance_km": 0.0,
                "transport_mode": "motorbike",
                "cost_per_sack": 1000,
                "cost_per_km": 10,
                "base_cost": 1110,
                "distance_cost": 0.0,
                "total_transport_cost": 1110.0,
                "note": "Detailed logistics calculation with kg to sacks conversion"
            }
        }
