"""
SMS endpoint for text message interface.
Parses SMS input and returns recommendations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.prediction_schema import SMSRequest, SMSResponse
from app.engine.decision_engine import DecisionEngine
from app.utils.helpers import parse_sms_input

router = APIRouter(prefix="/api", tags=["SMS"])
decision_engine = DecisionEngine()


@router.post("/sms", response_model=SMSResponse)
async def handle_sms(request: SMSRequest) -> dict:
    """
    Handle SMS message request.
    
    Expected format: "PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE"
    Example: "maize 100 Nairobi pickup yes"
    
    Args:
        request: SMSRequest with from_number and message
        
    Returns:
        SMSResponse with recommendation text
    """
    try:
        phone_number = request.from_number
        message = request.message
        
        # Parse SMS input
        parsed_data = parse_sms_input(message)
        
        # Validate parsed data
        if not all([
            parsed_data["produce"],
            parsed_data["quantity"],
            parsed_data["location"],
            parsed_data["transport_mode"]
        ]):
            error_response = (
                "Invalid format. Use: PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE\n"
                "Example: maize 100 Nairobi pickup yes"
            )
            return {
                "to_number": phone_number,
                "message": error_response
            }
        
        # Get recommendation
        recommendation = decision_engine.get_recommendation(parsed_data)
        
        # Format SMS response
        response_message = _format_sms_response(recommendation)
        
        return {
            "to_number": phone_number,
            "message": response_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS processing error: {str(e)}")


def _format_sms_response(recommendation: dict) -> str:
    """
    Format recommendation as SMS-friendly text.
    
    Args:
        recommendation: Recommendation dictionary
        
    Returns:
        Formatted SMS text
    """
    best_market = recommendation["best_market"]
    expected_price = recommendation["expected_price"]
    net_profit = recommendation["net_profit"]
    spoilage_risk = recommendation["spoilage_risk"]
    
    # SMS has character limits, so keep it concise
    message = (
        f"BEST MARKET: {best_market}\n"
        f"Price: KES {expected_price:.0f}/kg | "
        f"Profit: KES {net_profit:,.0f}\n"
        f"Risk: {spoilage_risk:.1f}% | "
        f"Action: Transport now"
    )
    
    return message


@router.get("/sms/sample")
async def get_sms_sample() -> dict:
    """
    Get sample SMS format.
    
    Returns:
        Sample SMS format and instructions
    """
    return {
        "format": "PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE",
        "example": "maize 100 Nairobi pickup yes",
        "parts": {
            "PRODUCE": "Type of produce (e.g., maize, tomato, beans)",
            "QUANTITY": "Amount in kg",
            "LOCATION": "County name (e.g., Nairobi, Kiambu)",
            "TRANSPORT_MODE": "motorbike, pickup, or lorry",
            "STORAGE": "yes or no"
        },
        "note": "All fields required. Send as single SMS message."
    }
