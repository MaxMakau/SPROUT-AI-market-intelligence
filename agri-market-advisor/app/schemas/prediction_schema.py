"""
Pydantic schemas for request and response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class PredictionRequest(BaseModel):
    """Request schema for market prediction."""
    
    produce: str = Field(..., description="Type of produce (e.g., maize, tomato, potato)")
    quantity: float = Field(..., gt=0, description="Quantity in kg")
    location: str = Field(..., description="Farmer's county/location in Kenya")
    transport_mode: str = Field(..., description="Transport mode: motorbike, pickup, or lorry")
    has_storage: bool = Field(default=False, description="Whether farmer has storage facility")
    moisture_level: Optional[float] = Field(default=None, description="Moisture level percentage")
    produce_grade: Optional[str] = Field(default=None, description="Grade: A, B, or C")
    
    class Config:
        schema_extra = {
            "example": {
                "produce": "maize",
                "quantity": 100,
                "location": "Nairobi",
                "transport_mode": "pickup",
                "has_storage": True,
                "moisture_level": 12.5,
                "produce_grade": "A"
            }
        }
        


class MarketBreakdown(BaseModel):
    """Breakdown of prediction for a single market."""
    
    market: str
    predicted_price: float = Field(..., description="Predicted price per unit (KES)")
    transport_cost: float = Field(..., description="Transport cost (KES)")
    spoilage_risk: float = Field(..., description="Spoilage risk percentage")
    expected_revenue: float = Field(..., description="Expected revenue (KES)")
    net_profit: float = Field(..., description="Net profit (KES)")


class PredictionResponse(BaseModel):
    """Response schema for market prediction."""
    
    best_market: str
    expected_price: float = Field(..., description="Price in best market (KES)")
    transport_cost: float = Field(..., description="Transport cost to best market (KES)")
    spoilage_risk: float = Field(..., description="Spoilage risk percentage")
    expected_revenue: float = Field(..., description="Total expected revenue (KES)")
    net_profit: float = Field(..., description="Net profit (KES)")
    breakdown: List[MarketBreakdown] = Field(..., description="Per-market breakdown")
    recommendation_reason: str = Field(..., description="Why this market is best")
    
    class Config:
        schema_extra = {
            "example": {
                "best_market": "Nairobi Central Market",
                "expected_price": 2500.0,
                "transport_cost": 500.0,
                "spoilage_risk": 5.0,
                "expected_revenue": 250000.0,
                "net_profit": 245000.0,
                "breakdown": [
                    {
                        "market": "Nairobi Central Market",
                        "predicted_price": 2500.0,
                        "transport_cost": 500.0,
                        "spoilage_risk": 5.0,
                        "expected_revenue": 250000.0,
                        "net_profit": 245000.0
                    }
                ],
                "recommendation_reason": "Highest net profit with lowest spoilage risk"
            }
        }


class PredictionJobResponse(PredictionResponse):
    """Prediction response extended with a job id for persisted results."""

    job_id: str

    class Config:
        schema_extra = {
            "example": {
                "job_id": "9f1a3c2b-4e6a-4a5d-9b3d-7d8c6f3a1b2c",
                "best_market": "Nairobi Central Market",
                "expected_price": 2500.0,
                "transport_cost": 500.0,
                "spoilage_risk": 5.0,
                "expected_revenue": 250000.0,
                "net_profit": 245000.0,
                "breakdown": [
                    {
                        "market": "Nairobi Central Market",
                        "predicted_price": 2500.0,
                        "transport_cost": 500.0,
                        "spoilage_risk": 5.0,
                        "expected_revenue": 250000.0,
                        "net_profit": 245000.0
                    }
                ],
                "recommendation_reason": "Highest net profit with lowest spoilage risk"
            }
        }


class LogisticsResponse(BaseModel):
    """Lightweight response for logistics/operations integration."""

    produce: str
    quantity: float = Field(..., description="Quantity in kg")
    location: str
    best_market: str
    distance_km: float = Field(..., description="Distance to best market in kilometers")
    transport_cost: float = Field(..., description="Transport cost to best market in KES")
    estimated_travel_time_hours: Optional[float] = Field(None, description="Estimated travel time in hours")
    note: Optional[str] = Field(None, description="Optional human readable note")

    class Config:
        schema_extra = {
            "example": {
                "produce": "maize",
                "quantity": 100,
                "location": "Nairobi",
                "best_market": "Nairobi Central Market",
                "distance_km": 12.5,
                "transport_cost": 500.0,
                "estimated_travel_time_hours": 0.3,
                "note": "Distance measured using OpenRouteService matrix API"
            }
        }


class LogisticsJobResponse(BaseModel):
    """Response for POST /api/logistics when a job is created.

    Returns a job id and the logistics payload so clients can store the id
    and later fetch it with `GET /api/logistics/{job_id}`.
    """

    job_id: str
    result: LogisticsResponse

    class Config:
        schema_extra = {
            "example": {
                "job_id": "9f1a3c2b-4e6a-4a5d-9b3d-7d8c6f3a1b2c",
                "result": {
                    "produce": "maize",
                    "quantity": 100,
                    "location": "Nairobi",
                    "best_market": "Nairobi Central Market",
                    "distance_km": 12.5,
                    "transport_cost": 500.0,
                    "estimated_travel_time_hours": 0.3,
                    "note": "Distance measured using OpenRouteService matrix API"
                }
            }
        }

class USSDRequest(BaseModel):
    """USSD request schema following Africa's Talking format."""
    
    sessionId: str
    phoneNumber: str
    text: str
    serviceCode: str


class USSDResponse(BaseModel):
    """USSD response schema."""
    
    response: str
    
    class Config:
        schema_extra = {
            "example": {
                "response": "END Best market is Nairobi Central Market with expected profit of KES 245,000"
            }
        }


class SMSRequest(BaseModel):
    """SMS request schema."""
    
    from_number: str
    message: str


class SMSResponse(BaseModel):
    """SMS response schema."""
    
    to_number: str
    message: str


class WhatsAppRequest(BaseModel):
    """WhatsApp message request schema."""
    
    from_number: str
    message: str


class WhatsAppResponse(BaseModel):
    """WhatsApp message response schema."""
    
    to_number: str
    message: str
