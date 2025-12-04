"""
Helper functions for data normalization and formatting.
"""

import re
from typing import Optional
from app.utils.constants import COUNTIES, PRODUCE_TYPES


def normalize_county_name(county: str) -> Optional[str]:
    """
    Normalize and validate county name.
    
    Args:
        county: Raw county name from user input
        
    Returns:
        Normalized county name or None if invalid
    """
    if not county:
        return None
    
    county = county.strip().lower()
    
    # Try exact match first
    for valid_county in COUNTIES:
        if valid_county.lower() == county:
            return valid_county
    
    # Try partial match
    for valid_county in COUNTIES:
        if county in valid_county.lower() or valid_county.lower() in county:
            return valid_county
    
    return None


def normalize_produce_name(produce: str) -> Optional[str]:
    """
    Normalize and validate produce name.
    
    Args:
        produce: Raw produce name from user input
        
    Returns:
        Normalized produce name or None if invalid
    """
    if not produce:
        return None
    
    produce = produce.strip().lower()
    
    # Try exact match first
    for valid_produce in PRODUCE_TYPES:
        if valid_produce.lower() == produce:
            return valid_produce
    
    # Try partial match
    for valid_produce in PRODUCE_TYPES:
        if produce in valid_produce.lower() or valid_produce.lower() in produce:
            return valid_produce
    
    return None


def normalize_transport_mode(mode: str) -> Optional[str]:
    """
    Normalize transport mode.
    
    Args:
        mode: Raw transport mode from user input
        
    Returns:
        Normalized transport mode or None if invalid
    """
    if not mode:
        return None
    
    mode = mode.strip().lower()
    valid_modes = ["motorbike", "pickup", "lorry"]
    
    for valid_mode in valid_modes:
        if valid_mode in mode or mode in valid_mode:
            return valid_mode
    
    return None


def format_currency(amount: float) -> str:
    """
    Format currency value with KES prefix.
    
    Args:
        amount: Amount in KES
        
    Returns:
        Formatted currency string
    """
    return f"KES {amount:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.1f}%"


def format_ussd_response(text: str, end: bool = True) -> str:
    """
    Format response for USSD.
    
    Args:
        text: Response text
        end: Whether to end session
        
    Returns:
        Formatted USSD response
    """
    prefix = "END" if end else "CON"
    return f"{prefix} {text}"


def parse_sms_input(message: str) -> dict:
    """
    Parse SMS message into structured input.
    Simple grammar: "produce quantity location transport_mode storage"
    
    Args:
        message: SMS message text
        
    Returns:
        Dictionary with parsed fields
    """
    parts = message.strip().split()
    
    result = {
        "produce": None,
        "quantity": None,
        "location": None,
        "transport_mode": None,
        "has_storage": False
    }
    
    if len(parts) >= 1:
        result["produce"] = normalize_produce_name(parts[0])
    
    if len(parts) >= 2:
        try:
            result["quantity"] = float(parts[1])
        except ValueError:
            pass
    
    if len(parts) >= 3:
        result["location"] = normalize_county_name(parts[2])
    
    if len(parts) >= 4:
        result["transport_mode"] = normalize_transport_mode(parts[3])
    
    if len(parts) >= 5:
        result["has_storage"] = parts[4].lower() in ["yes", "y", "true", "1"]
    
    return result


def calculate_transport_time_hours(distance_km: float, mode: str) -> float:
    """
    Estimate transport time in hours based on distance and mode.
    
    Args:
        distance_km: Distance in kilometers
        mode: Transport mode
        
    Returns:
        Estimated time in hours
    """
    # Average speeds (km/h)
    speeds = {
        "motorbike": 40,
        "pickup": 50,
        "lorry": 40
    }
    
    speed = speeds.get(mode, 50)
    return distance_km / speed


def estimate_distance_between_counties(from_county: str, to_county: str) -> float:
    """
    Estimate distance between two counties (mock implementation).
    
    Args:
        from_county: Starting county
        to_county: Destination county
        
    Returns:
        Estimated distance in km
    """
    if from_county == to_county:
        return 5.0  # Intra-county distance
    
    # Mock distance matrix - in production, use Google Maps API
    distances = {
        ("Nairobi", "Kiambu"): 25,
        ("Nairobi", "Muranga"): 50,
        ("Nairobi", "Mombasa"): 480,
        ("Nairobi", "Kisumu"): 400,
        ("Kiambu", "Muranga"): 40,
    }
    
    key = tuple(sorted([from_county, to_county]))
    return distances.get(key, 100.0)  # Default 100 km if not found


def error_response(message: str) -> dict:
    """
    Generate standardized error response.
    
    Args:
        message: Error message
        
    Returns:
        Error response dictionary
    """
    return {
        "status": "error",
        "message": message
    }


def success_response(data: dict) -> dict:
    """
    Generate standardized success response.
    
    Args:
        data: Response data
        
    Returns:
        Success response dictionary
    """
    return {
        "status": "success",
        "data": data
    }
