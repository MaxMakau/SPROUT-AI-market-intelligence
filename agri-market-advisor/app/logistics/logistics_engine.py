"""
Logistics engine - core module for transport recommendation and cost calculation.
Deterministic rules for transport mode selection and cost computation.
"""


def round_to_meaningful(value: float, decimal_places: int = 1) -> float:
    """
    Round numbers to meaningful metrics.
    
    Rules:
    - 0.1-0.5 → 0.5
    - 0.6-0.9 → 1.0
    - Whole numbers remain as is
    - Other decimals rounded to 1 decimal place
    
    Args:
        value: The numeric value to round
        decimal_places: Number of decimal places (default 1)
        
    Returns:
        Rounded float value with meaningful metrics
    """
    if value == int(value):
        return float(int(value))
    
    integer_part = int(value)
    decimal_part = value - integer_part
    
    # If decimal is between 0.1 and 0.5, round to 0.5
    if 0.1 <= decimal_part <= 0.5:
        return integer_part + 0.5
    
    # If decimal is between 0.6 and 0.9, round to next integer
    if 0.6 <= decimal_part <= 0.9:
        return float(integer_part + 1)
    
    # Otherwise, round to specified decimal places
    return round(value, decimal_places)


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


def kg_to_sacks(quantity_kg: float, kg_per_sack: int = 90) -> float:
    """
    Convert quantity from kilograms to sacks.
    
    Args:
        quantity_kg: Quantity in kilograms
        kg_per_sack: Standard sack size (default 90 kg)
        
    Returns:
        Number of sacks (as float)
    """
    return quantity_kg / kg_per_sack


def compute_transport_cost_detailed(
    quantity_kg: float,
    distance_km: float,
    kg_per_sack: int = 90
) -> dict:
    """
    Compute detailed transport cost breakdown.
    
    Converts quantity from kg to sacks, recommends transport mode,
    and calculates cost based on both quantity (per-sack) and distance.
    
    Cost formula:
    - Base cost per sack: varies by transport mode (motorbike: 1000, pickup: 700, lorry: 400)
    - Distance cost per km: 10 KES per km (additional)
    - Total = (quantity_sacks * base_cost_per_sack) + (distance_km * distance_cost_per_km)
    
    Args:
        quantity_kg: Quantity in kilograms
        distance_km: Distance to market in kilometers
        kg_per_sack: Standard sack size (default 90 kg per sack)
        
    Returns:
        Dictionary with detailed breakdown:
        - quantity_sacks: float (rounded to meaningful metrics)
        - transport_mode: str
        - cost_per_sack: int (base cost without distance)
        - cost_per_km: int (distance-based cost)
        - distance_km: float (rounded to meaningful metrics)
        - base_cost: int (quantity_sacks * cost_per_sack)
        - distance_cost: float (distance_km * cost_per_km, rounded)
        - total_cost: float (base_cost + distance_cost, rounded)
    """
    quantity_sacks = kg_to_sacks(quantity_kg, kg_per_sack)
    
    # Round quantity sacks to meaningful metrics
    quantity_sacks_rounded = round_to_meaningful(quantity_sacks)
    
    # Use rounded sacks for transport mode recommendation
    mode = recommend_transport(int(quantity_sacks_rounded) if quantity_sacks_rounded >= 1 else 1)
    
    # Get base cost per sack
    rates_per_sack = {
        "motorbike": 1000,
        "pickup": 700,
        "lorry": 400,
    }
    cost_per_sack = rates_per_sack[mode]
    
    # Distance cost: 10 KES per km
    cost_per_km = 10
    
    # Round distance to meaningful metrics
    distance_km_rounded = round_to_meaningful(distance_km)
    
    # Calculate costs using rounded values
    base_cost = cost_per_sack * quantity_sacks_rounded
    distance_cost = distance_km_rounded * cost_per_km
    total_cost = base_cost + distance_cost
    
    return {
        "quantity_sacks": quantity_sacks_rounded,
        "transport_mode": mode,
        "cost_per_sack": cost_per_sack,
        "cost_per_km": cost_per_km,
        "distance_km": distance_km_rounded,
        "base_cost": int(base_cost),
        "distance_cost": int(distance_cost),
        "total_cost": int(total_cost),
    }


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
