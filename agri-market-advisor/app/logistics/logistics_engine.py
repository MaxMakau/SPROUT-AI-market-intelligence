"""
Logistics engine - core module for transport recommendation and cost calculation.
Deterministic rules for transport mode selection and cost computation.
"""


def recommend_transport(quantity_sacks: int) -> str:
    """
    Recommend transport method based on quantity of sacks.
    
    Rules:
    - quantity_sacks > 10 → "lorry"
    - 3 < quantity_sacks <= 10 → "pickup"
    - quantity_sacks <= 3 → "motorbike"
    
    Args:
        quantity_sacks: Number of sacks to transport
        
    Returns:
        Recommended transport mode as string
    """
    if quantity_sacks > 10:
        return "lorry"
    if quantity_sacks > 3:
        return "pickup"
    return "motorbike"


def compute_transport_cost(quantity_sacks: int, mode: str) -> int:
    """
    Compute transport cost based on quantity and transport mode.
    
    Rate per sack:
    - "motorbike" → 1000 KES per sack
    - "pickup" → 700 KES per sack
    - "lorry" → 400 KES per sack
    
    Args:
        quantity_sacks: Number of sacks
        mode: Transport mode (motorbike, pickup, or lorry)
        
    Returns:
        Total transport cost in KES
        
    Raises:
        KeyError: If mode is not in rates dictionary
    """
    rates = {
        "motorbike": 1000,
        "pickup": 700,
        "lorry": 400,
    }
    rate = rates[mode]
    return rate * quantity_sacks


def build_logistics_plan(
    quantity_sacks: int,
    distance_km: float,
    best_market_location: str,
    market_price: float
) -> dict:
    """
    Build a comprehensive logistics plan based on input parameters.
    
    Combines transport recommendation and cost calculation with market information.
    
    Args:
        quantity_sacks: Number of sacks to transport
        distance_km: Distance to market in kilometers
        best_market_location: Name of the best market location
        market_price: Expected market price in KES per unit
        
    Returns:
        Dictionary with logistics plan details:
        - transport_mode: str
        - transport_cost_kes: int
        - distance_km: float
        - best_market_location: str
        - market_price: float
    """
    mode = recommend_transport(quantity_sacks)
    cost = compute_transport_cost(quantity_sacks, mode)

    return {
        "transport_mode": mode,
        "transport_cost_kes": cost,
        "distance_km": distance_km,
        "best_market_location": best_market_location,
        "market_price": market_price,
    }
