"""
Main prediction API endpoint.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.prediction_schema import (
    PredictionRequest,
    PredictionResponse,
    LogisticsResponse,
    LogisticsJobResponse,
    PredictionJobResponse,
)
from app.engine.decision_engine import DecisionEngine
from app.services.prediction_store import save_result, get_result

router = APIRouter(prefix="/api", tags=["Prediction"])
decision_engine = DecisionEngine()


@router.post("/predict", response_model=PredictionJobResponse)
async def predict_market(request: PredictionRequest) -> dict:
    """
    Main prediction endpoint.
    
    Accepts farmer input and returns best market recommendation
    with detailed breakdown and profit analysis.
    
    Args:
        request: PredictionRequest with produce, quantity, location, etc.
        
    Returns:
        PredictionResponse with best market and detailed breakdown
    """
    try:
        # Convert request to dictionary
        input_data = {
            "produce": request.produce.lower(),
            "quantity": request.quantity,
            "location": request.location,
            "transport_mode": request.transport_mode.lower(),
            "has_storage": request.has_storage,
            "moisture_level": request.moisture_level,
            "produce_grade": request.produce_grade or "B"
        }
        
        # Validate input
        is_valid, error_msg = decision_engine.validate_input(input_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get recommendation
        recommendation = decision_engine.get_recommendation(input_data)

        # Persist the prediction + input and return job id alongside result
        payload = {"input": input_data, "prediction": recommendation}
        job_id = save_result(payload)

        # Build response: prediction fields + job_id
        response = recommendation.copy()
        response["job_id"] = job_id

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prediction: {str(e)}")


@router.post("/logistics", response_model=LogisticsJobResponse)
async def get_logistics_info(request: PredictionRequest) -> dict:
    """
    Lightweight endpoint for logistics systems.

    Returns the produce, quantity, origin location, best market,
    distance to best market (km), transport cost (KES), and estimated travel time (hours).
    """
    try:
        input_data = {
            "produce": request.produce.lower(),
            "quantity": request.quantity,
            "location": request.location,
            "transport_mode": request.transport_mode.lower(),
            "has_storage": request.has_storage,
            "moisture_level": request.moisture_level,
            "produce_grade": request.produce_grade or "B"
        }

        # Validate input
        is_valid, error_msg = decision_engine.validate_input(input_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Reuse decision engine recommendation
        recommendation = decision_engine.get_recommendation(input_data)

        additional = recommendation.get("additional_info", {})

        result = {
            "produce": additional.get("produce", input_data["produce"]),
            "quantity": additional.get("quantity", input_data["quantity"]),
            "location": additional.get("location", input_data["location"]),
            "best_market": recommendation.get("best_market"),
            "distance_km": additional.get("distance_to_best_market_km"),
            "transport_cost": recommendation.get("transport_cost"),
            "estimated_travel_time_hours": additional.get("estimated_travel_time_hours"),
            "note": "Use this data for logistics planning."
        }

        # Persist the result and return job id + payload
        job_id = save_result({"input": input_data, "result": result})

        return {"job_id": job_id, "result": result}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating logistics info: {str(e)}")


@router.get("/logistics/{job_id}", response_model=LogisticsResponse)
async def fetch_logistics_job(job_id: str) -> dict:
    """Fetch stored logistics result by job id."""
    rec = get_result(job_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Job not found or expired")

    # The payload may be saved in different shapes depending on endpoint:
    # - logistics endpoint saves: {"input": ..., "result": {...}}
    # - predict endpoint saves: {"input": ..., "prediction": {...}}
    # Be tolerant and return whichever is present. Avoid returning None
    # which would fail Pydantic validation for the response model.
    if isinstance(rec, dict):
        if rec.get("result") is not None:
            return rec.get("result")
        if rec.get("prediction") is not None:
            # Build a LogisticsResponse-shaped object from prediction payload
            pred = rec.get("prediction")
            additional = pred.get("additional_info", {}) if isinstance(pred, dict) else {}

            logistics = {
                "produce": additional.get("produce") or additional.get("produce", None),
                "quantity": additional.get("quantity") or additional.get("quantity", None),
                "location": additional.get("location") or additional.get("location", None),
                "best_market": pred.get("best_market"),
                "distance_km": additional.get("distance_to_best_market_km") or additional.get("distance_km") or 0.0,
                "transport_cost": pred.get("transport_cost"),
                "estimated_travel_time_hours": additional.get("estimated_travel_time_hours"),
                "note": additional.get("note") or "Converted from prediction payload"
            }

            return logistics

    # Fallback: return the whole record if it looks like a payload
    return rec


@router.get("/predict/{job_id}")
async def fetch_prediction_job(job_id: str) -> dict:
    """Fetch stored prediction by job id."""
    rec = get_result(job_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Job not found or expired")

    if isinstance(rec, dict):
        if rec.get("prediction") is not None:
            return rec.get("prediction")
        if rec.get("result") is not None:
            return rec.get("result")

    return rec


@router.get("/predict/markets")
async def get_available_markets() -> dict:
    """
    Get list of available markets.
    
    Returns:
        Dictionary with available markets
    """
    from app.utils.constants import MARKET_LOCATIONS
    
    return {
        "total_markets": len(MARKET_LOCATIONS),
        "markets": MARKET_LOCATIONS
    }


@router.get("/predict/produce")
async def get_available_produce() -> dict:
    """
    Get list of supported produce types.
    
    Returns:
        Dictionary with supported produce
    """
    from app.utils.constants import PRODUCE_TYPES
    
    return {
        "total_produce": len(PRODUCE_TYPES),
        "produce": sorted(PRODUCE_TYPES)
    }


@router.get("/predict/transport-modes")
async def get_transport_modes() -> dict:
    """
    Get available transport modes.
    
    Returns:
        Dictionary with transport modes and costs
    """
    from app.utils.constants import TRANSPORT_MODES
    
    return {
        "transport_modes": [
            {
                "mode": mode,
                "cost_per_km_kes": cost
            }
            for mode, cost in TRANSPORT_MODES.items()
        ]
    }


@router.post("/shipments")
async def create_shipment(shipment: dict) -> dict:
    """
    Minimal shipment creation endpoint to persist a shipment request.

    This endpoint stores the incoming shipment payload in the lightweight
    prediction store and returns a `shipment_id` that clients can use as a
    reference. It is intentionally simple to act as a scaffold for frontend
    integration; a full shipment management system (assignment, tracking,
    carrier integration) can be implemented later.
    """
    try:
        # Save the shipment payload and return an id
        shipment_id = save_result({"shipment": shipment})
        return {"shipment_id": shipment_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating shipment: {str(e)}")
