"""
Main prediction API endpoint.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse
from app.engine.decision_engine import DecisionEngine

router = APIRouter(prefix="/api", tags=["Prediction"])
decision_engine = DecisionEngine()


@router.post("/predict", response_model=PredictionResponse)
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
        
        return recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prediction: {str(e)}")


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
