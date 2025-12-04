"""
WhatsApp endpoint for WhatsApp messaging interface.
Parses WhatsApp messages and returns recommendations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.prediction_schema import WhatsAppRequest, WhatsAppResponse
from app.engine.decision_engine import DecisionEngine
from app.utils.helpers import parse_sms_input, format_currency

router = APIRouter(prefix="/api", tags=["WhatsApp"])
decision_engine = DecisionEngine()

# WhatsApp session storage (in production, use proper database)
whatsapp_sessions = {}


@router.post("/whatsapp", response_model=WhatsAppResponse)
async def handle_whatsapp(request: WhatsAppRequest) -> dict:
    """
    Handle WhatsApp message request.
    
    Expected format: "PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE"
    Example: "maize 100 Nairobi pickup yes"
    
    Args:
        request: WhatsAppRequest with from_number and message
        
    Returns:
        WhatsAppResponse with recommendation
    """
    try:
        phone_number = request.from_number
        message = request.message.strip()
        
        # Parse WhatsApp input
        parsed_data = parse_sms_input(message)
        
        # Validate parsed data
        if not all([
            parsed_data["produce"],
            parsed_data["quantity"],
            parsed_data["location"],
            parsed_data["transport_mode"]
        ]):
            error_response = (
                "📋 Invalid format\n\n"
                "Please use: PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE\n\n"
                "Example:\n"
                "maize 100 Nairobi pickup yes\n\n"
                "Options:\n"
                "• Transport: motorbike, pickup, lorry\n"
                "• Storage: yes or no"
            )
            return {
                "to_number": phone_number,
                "message": error_response
            }
        
        # Get recommendation
        recommendation = decision_engine.get_recommendation(parsed_data)
        
        # Format WhatsApp response (can use emoji and formatting)
        response_message = _format_whatsapp_response(recommendation)
        
        return {
            "to_number": phone_number,
            "message": response_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatsApp error: {str(e)}")


def _format_whatsapp_response(recommendation: dict) -> str:
    """
    Format recommendation as WhatsApp-friendly message.
    Can use emoji and rich formatting.
    
    Args:
        recommendation: Recommendation dictionary
        
    Returns:
        Formatted WhatsApp message
    """
    best_market = recommendation["best_market"]
    expected_price = recommendation["expected_price"]
    net_profit = recommendation["net_profit"]
    spoilage_risk = recommendation["spoilage_risk"]
    produce = recommendation["additional_info"]["produce"]
    quantity = recommendation["additional_info"]["quantity"]
    
    # Create detailed WhatsApp message
    message = (
        f"🌾 *Sprout AI Market Recommendation*\n\n"
        f"📍 *Best Market:* {best_market}\n"
        f"🥕 *Produce:* {produce.capitalize()}\n"
        f"⚖️ *Quantity:* {quantity} kg\n\n"
        f"💰 *Financial Summary*\n"
        f"├ Price: KES {expected_price:,.2f}/kg\n"
        f"├ Expected Profit: KES {net_profit:,.2f}\n"
        f"└ Profit Margin: {recommendation['profit_margin_percent']:.1f}%\n\n"
        f"⚠️ *Risk Assessment*\n"
        f"└ Spoilage Risk: {spoilage_risk:.1f}%\n\n"
        f"✅ *Recommendation:*\n"
        f"{recommendation['recommendation_reason']}\n\n"
        f"_Powered by Sprout AI_"
    )
    
    return message


@router.post("/whatsapp/broadcast")
async def send_whatsapp_broadcast(numbers: list, message: str) -> dict:
    """
    Send broadcast message to multiple WhatsApp numbers.
    
    Args:
        numbers: List of phone numbers
        message: Message to send
        
    Returns:
        Status of broadcast
    """
    # Mock implementation
    return {
        "status": "broadcast_queued",
        "recipients": len(numbers),
        "message_length": len(message)
    }


@router.get("/whatsapp/template")
async def get_whatsapp_template() -> dict:
    """
    Get WhatsApp message template.
    
    Returns:
        Template for WhatsApp message
    """
    return {
        "format": "PRODUCE QUANTITY LOCATION TRANSPORT_MODE STORAGE",
        "example": "maize 100 Nairobi pickup yes",
        "valid_produce": [
            "maize", "beans", "tomato", "potato", "onion", "pepper",
            "cabbage", "carrots", "milk", "eggs", "chicken"
        ],
        "valid_locations": [
            "Nairobi", "Kiambu", "Muranga", "Mombasa", "Kisumu",
            "Nakuru", "Kericho", "Nyeri"
        ],
        "valid_transport": ["motorbike", "pickup", "lorry"],
        "note": "Send message to WhatsApp bot number"
    }
