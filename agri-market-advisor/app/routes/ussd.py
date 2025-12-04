"""
USSD endpoint for Africa's Talking USSD format.
Implements multi-step menu for farmer input.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.prediction_schema import USSDRequest, USSDResponse
from app.engine.decision_engine import DecisionEngine
from app.utils.helpers import (
    normalize_produce_name, normalize_county_name,
    normalize_transport_mode, format_currency, format_ussd_response
)
from app.utils.constants import PRODUCE_TYPES, COUNTIES, MARKET_LOCATIONS

router = APIRouter(prefix="/api", tags=["USSD"])
decision_engine = DecisionEngine()

# Simple in-memory session store (in production, use Redis)
ussd_sessions = {}


@router.post("/ussd", response_model=USSDResponse)
async def handle_ussd(request: USSDRequest) -> dict:
    """
    Handle USSD request following Africa's Talking format.
    
    Implements multi-step menu:
    1. Ask for produce
    2. Ask for quantity
    3. Ask for location
    4. Ask for transport mode
    5. Ask about storage
    6. Return recommendation
    
    Args:
        request: USSDRequest with sessionId, phoneNumber, text, serviceCode
        
    Returns:
        USSDResponse with formatted menu or result
    """
    try:
        session_id = request.sessionId
        phone_number = request.phoneNumber
        user_input = request.text.strip()
        
        # Initialize or retrieve session
        if session_id not in ussd_sessions:
            ussd_sessions[session_id] = {
                "step": 0,
                "phone_number": phone_number,
                "data": {}
            }
        
        session = ussd_sessions[session_id]
        step = session["step"]
        data = session["data"]
        
        # Process based on current step
        if step == 0:
            # Initial menu - ask for produce
            session["step"] = 1
            response_text = (
                "Welcome to Sprout AI - Agri-Market Advisor\n"
                "Enter produce name:\n"
                "e.g., maize, tomato, beans, potato, onion"
            )
        
        elif step == 1:
            # Validate produce
            produce = normalize_produce_name(user_input)
            if not produce:
                response_text = (
                    "Invalid produce. Please try again:\n"
                    "e.g., maize, tomato, beans, potato"
                )
            else:
                data["produce"] = produce
                session["step"] = 2
                response_text = "Enter quantity in kg:"
        
        elif step == 2:
            # Get quantity
            try:
                quantity = float(user_input)
                if quantity <= 0:
                    raise ValueError()
                data["quantity"] = quantity
                session["step"] = 3
                response_text = (
                    "Enter your location (county):\n"
                    "e.g., Nairobi, Kiambu, Muranga"
                )
            except ValueError:
                response_text = "Invalid quantity. Enter a positive number:"
        
        elif step == 3:
            # Get location
            location = normalize_county_name(user_input)
            if not location:
                response_text = "Invalid location. Try again:"
            else:
                data["location"] = location
                session["step"] = 4
                response_text = (
                    "Select transport mode:\n"
                    "1. Motorbike\n"
                    "2. Pickup\n"
                    "3. Lorry"
                )
        
        elif step == 4:
            # Get transport mode
            mode_map = {"1": "motorbike", "2": "pickup", "3": "lorry"}
            transport_mode = mode_map.get(user_input.strip())
            
            if not transport_mode:
                transport_mode = normalize_transport_mode(user_input)
            
            if not transport_mode:
                response_text = (
                    "Invalid mode. Choose:\n"
                    "1. Motorbike\n"
                    "2. Pickup\n"
                    "3. Lorry"
                )
            else:
                data["transport_mode"] = transport_mode
                session["step"] = 5
                response_text = (
                    "Do you have storage facility?\n"
                    "1. Yes\n"
                    "2. No"
                )
        
        elif step == 5:
            # Get storage availability
            storage_map = {"1": True, "2": False, "yes": True, "no": False, "y": True, "n": False}
            has_storage = storage_map.get(user_input.lower().strip())
            
            if has_storage is None:
                response_text = (
                    "Invalid input. Enter:\n"
                    "1. Yes (have storage)\n"
                    "2. No (no storage)"
                )
            else:
                data["has_storage"] = has_storage
                
                # All data collected - get recommendation
                try:
                    recommendation = decision_engine.get_recommendation(data)
                    
                    best_market = recommendation["best_market"]
                    net_profit = recommendation["net_profit"]
                    expected_price = recommendation["expected_price"]
                    spoilage_risk = recommendation["spoilage_risk"]
                    
                    response_text = (
                        f"BEST MARKET: {best_market}\n"
                        f"Expected Price: KES {expected_price:.0f}/kg\n"
                        f"Expected Profit: KES {net_profit:,.0f}\n"
                        f"Spoilage Risk: {spoilage_risk:.1f}%\n"
                        f"Recommended: Transport immediately"
                    )
                    session["step"] = 6  # End
                    
                except Exception as e:
                    response_text = f"Error processing recommendation: {str(e)}"
                    session["step"] = 6
        
        else:
            # End session
            response_text = (
                "Thank you for using Sprout AI!\n"
                "Dial *384*88888# to make another query"
            )
            del ussd_sessions[session_id]
        
        # Format as USSD response (END if step >= 6, else CON)
        should_end = session["step"] >= 6
        formatted_response = format_ussd_response(response_text, end=should_end)
        
        return {"response": formatted_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"USSD error: {str(e)}")


@router.post("/ussd/reset")
async def reset_ussd_session(session_id: str) -> dict:
    """
    Reset a USSD session.
    
    Args:
        session_id: Session ID to reset
        
    Returns:
        Status message
    """
    if session_id in ussd_sessions:
        del ussd_sessions[session_id]
        return {"status": "Session reset", "session_id": session_id}
    return {"status": "Session not found", "session_id": session_id}
