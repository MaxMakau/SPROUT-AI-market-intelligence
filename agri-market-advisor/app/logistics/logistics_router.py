"""
Logistics router - API endpoints for transport recommendations.
"""

from fastapi import APIRouter, HTTPException
from .logistics_schema import LogisticsRequest, LogisticsResponse, DetailedLogisticsResponse
from .logistics_engine import build_logistics_plan, compute_transport_cost_detailed
from app.services.prediction_store import get_result

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


@router.get("/job/{job_id}/details", response_model=DetailedLogisticsResponse)
async def get_detailed_logistics(job_id: str) -> dict:
    """
    Get detailed logistics calculation for a stored job.
    
    Fetches the stored prediction/logistics data by job_id and performs
    detailed transport cost calculation including:
    - Conversion from kg to sacks (1 sack = 90 kg)
    - Transport mode recommendation based on quantity
    - Cost breakdown: per-sack cost + distance cost
    
    Args:
        job_id: UUID of the stored prediction/logistics job
        
    Returns:
        DetailedLogisticsResponse with full cost breakdown
        
    Raises:
        HTTPException: 404 if job not found or expired
    """
    try:
        # Fetch stored result
        rec = get_result(job_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Job not found or expired")
        
        # Extract the logistics/prediction data
        if isinstance(rec, dict):
            # Handle both logistics endpoint and prediction endpoint payloads
            if rec.get("result"):
                payload = rec.get("result")
            elif rec.get("prediction"):
                pred = rec.get("prediction")
                additional = pred.get("additional_info", {}) if isinstance(pred, dict) else {}
                payload = {
                    "produce": additional.get("produce") or pred.get("produce"),
                    "quantity": additional.get("quantity") or payload.get("quantity"),
                    "location": additional.get("location") or payload.get("location"),
                    "best_market": pred.get("best_market"),
                    "distance_km": additional.get("distance_to_best_market_km") or additional.get("distance_km") or 0.0,
                }
            else:
                payload = rec
        else:
            raise HTTPException(status_code=400, detail="Invalid job data format")
        
        # Validate required fields
        required_fields = ["produce", "quantity", "location", "best_market", "distance_km"]
        for field in required_fields:
            if field not in payload or payload[field] is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job data missing required field: {field}"
                )
        
        # Perform detailed logistics calculation
        quantity_kg = payload.get("quantity")
        distance_km = payload.get("distance_km", 0.0)
        
        logistics_detail = compute_transport_cost_detailed(
            quantity_kg=quantity_kg,
            distance_km=distance_km,
            kg_per_sack=90
        )
        
        # Build response
        response = {
            "produce": payload.get("produce"),
            "quantity_kg": quantity_kg,
            "quantity_sacks": logistics_detail["quantity_sacks"],
            "location": payload.get("location"),
            "best_market": payload.get("best_market"),
            "distance_km": distance_km,
            "transport_mode": logistics_detail["transport_mode"],
            "cost_per_sack": logistics_detail["cost_per_sack"],
            "cost_per_km": logistics_detail["cost_per_km"],
            "base_cost": logistics_detail["base_cost"],
            "distance_cost": logistics_detail["distance_cost"],
            "total_transport_cost": logistics_detail["total_cost"],
            "note": f"Calculated {logistics_detail['quantity_sacks']} sacks from {quantity_kg}kg using 1 sack = 90kg"
        }
        
        return DetailedLogisticsResponse(**response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating detailed logistics: {str(e)}"
        )
