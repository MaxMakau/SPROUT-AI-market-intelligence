"""
Logistics router - API endpoints for transport recommendations.
"""

from fastapi import APIRouter
from .logistics_schema import LogisticsRequest, LogisticsResponse
from .logistics_engine import build_logistics_plan

router = APIRouter(prefix="/logistics", tags=["Logistics"])


@router.post("/recommend", response_model=LogisticsResponse)
def recommend_logistics(data: LogisticsRequest) -> dict:
    """
    Recommend transport method and calculate transport cost.
    
    Takes farmer's produce quantity, distance to market, and market information,
    then returns optimal transport recommendation with cost breakdown.
    
    Args:
        data: LogisticsRequest with quantity_sacks, distance_km, best_market_location, market_price
        
    Returns:
        LogisticsResponse with transport_mode, transport_cost_kes, and other details
    """
    plan = build_logistics_plan(
        quantity_sacks=data.quantity_sacks,
        distance_km=data.distance_km,
        best_market_location=data.best_market_location,
        market_price=data.market_price
    )
    return LogisticsResponse(**plan)
