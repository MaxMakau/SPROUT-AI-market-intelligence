"""
Market negotiation engine for calculating bulk pricing and negotiation leverage.
Provides insights on how volume improves farmer profitability.
"""

from typing import Dict, List, Optional


def calculate_bulk_pricing(
    base_price_per_kg: float,
    total_quantity_kg: float,
    produce_type: str = None
) -> Dict[str, float]:
    """
    Calculate negotiated bulk prices based on quantity.
    
    Pricing Tiers (example for maize):
    - ≤100 kg: -0% (retail price)
    - 101-500 kg: +2% premium
    - 501-1000 kg: +4% premium
    - 1001-2000 kg: +6% premium
    - >2000 kg: +8% premium
    
    Args:
        base_price_per_kg: Retail/individual farmer price
        total_quantity_kg: Total consolidated quantity
        produce_type: Type of produce (for custom pricing tiers)
        
    Returns:
        Dictionary with price tiers and negotiated price
    """
    # Define pricing tiers
    pricing_tiers = {
        "default": [
            (100, 0.00),      # ≤100 kg: 0% premium
            (500, 0.02),      # ≤500 kg: 2% premium
            (1000, 0.04),     # ≤1000 kg: 4% premium
            (2000, 0.06),     # ≤2000 kg: 6% premium
            (float('inf'), 0.08)  # >2000 kg: 8% premium
        ],
        "maize": [
            (100, 0.00),
            (500, 0.02),
            (1000, 0.04),
            (2000, 0.06),
            (float('inf'), 0.08)
        ],
        "beans": [
            (100, 0.00),
            (300, 0.03),
            (800, 0.05),
            (1500, 0.07),
            (float('inf'), 0.10)
        ],
        "tomato": [
            (100, 0.00),
            (200, 0.01),  # Small premium for tomatoes
            (500, 0.02),
            (1000, 0.03),
            (float('inf'), 0.04)
        ],
    }
    
    # Get appropriate pricing tier
    tiers = pricing_tiers.get(produce_type.lower() if produce_type else "default", pricing_tiers["default"])
    
    # Find applicable premium
    premium = 0
    for tier_limit, tier_premium in tiers:
        if total_quantity_kg <= tier_limit:
            premium = tier_premium
            break
    
    negotiated_price = base_price_per_kg * (1 + premium)
    
    return {
        "base_price_per_kg": round(base_price_per_kg, 2),
        "total_quantity_kg": total_quantity_kg,
        "negotiated_price_per_kg": round(negotiated_price, 2),
        "price_premium_percent": round(premium * 100, 1),
        "additional_revenue_per_kg": round(negotiated_price - base_price_per_kg, 2),
        "total_additional_revenue": round((negotiated_price - base_price_per_kg) * total_quantity_kg, 2),
    }


def calculate_negotiation_leverage(
    total_quantity_kg: float,
    farmer_count: int,
    produce_type: str = None
) -> Dict[str, str]:
    """
    Generate negotiation messaging/leverage information.
    Shows what farmers can use to negotiate with buyers.
    
    Args:
        total_quantity_kg: Total consolidated quantity
        farmer_count: Number of farmers in group
        produce_type: Type of produce
        
    Returns:
        Dictionary with negotiation talking points
    """
    # Convert to sacks for more intuitive messaging
    sacks = round(total_quantity_kg / 90, 1)
    
    # Generate leverage points
    leverage = {
        "volume_message": f"Consolidated shipment of {sacks} sacks ({total_quantity_kg:.0f}kg) from {farmer_count} farmers",
        "consistency_message": f"Regular weekly volumes of {sacks} sacks available",
        "quality_message": f"Standardized quality across {farmer_count} farmer network",
        "reliability_message": "Organized group ensures consistent delivery schedules",
        "logistics_message": f"Single delivery point instead of {farmer_count} separate trips",
    }
    
    # Add size-based messaging
    if sacks < 5:
        leverage["market_category"] = "Small Consolidation"
        leverage["negotiation_power"] = "Moderate - emphasize reliability and consistency"
    elif sacks < 15:
        leverage["market_category"] = "Medium Consolidation"
        leverage["negotiation_power"] = "Good - highlight bulk quantity and standard quality"
    elif sacks < 30:
        leverage["market_category"] = "Large Consolidation"
        leverage["negotiation_power"] = "Strong - negotiate volume discounts and preferential pricing"
    else:
        leverage["market_category"] = "Bulk Shipment"
        leverage["negotiation_power"] = "Very Strong - consider direct buyer agreements"
    
    return leverage


def calculate_profit_improvement(
    individual_revenues: List[float],
    individual_costs: List[float],
    consolidated_cost: float,
    bulk_price_revenue: float
) -> Dict[str, float]:
    """
    Calculate how much profit improves with clustering.
    
    Args:
        individual_revenues: Revenue for each farmer selling individually
        individual_costs: Transport cost for each farmer
        consolidated_cost: Total transport cost if consolidated
        bulk_price_revenue: Total revenue with bulk pricing
        
    Returns:
        Profit improvement breakdown
    """
    farmer_count = len(individual_revenues)
    
    # Individual scenario
    individual_total_revenue = sum(individual_revenues)
    individual_total_cost = sum(individual_costs)
    individual_total_profit = individual_total_revenue - individual_total_cost
    individual_avg_profit = individual_total_profit / farmer_count if farmer_count > 0 else 0
    
    # Consolidated scenario
    consolidated_cost_per_farmer = consolidated_cost / farmer_count if farmer_count > 0 else 0
    consolidated_total_cost = consolidated_cost
    consolidated_total_profit = bulk_price_revenue - consolidated_total_cost
    consolidated_avg_profit = consolidated_total_profit / farmer_count if farmer_count > 0 else 0
    
    # Improvement metrics
    improvement_per_farmer = consolidated_avg_profit - individual_avg_profit
    improvement_percent = (improvement_per_farmer / individual_avg_profit * 100) if individual_avg_profit > 0 else 0
    
    return {
        "individual_scenario": {
            "total_revenue": round(individual_total_revenue, 2),
            "total_cost": round(individual_total_cost, 2),
            "total_profit": round(individual_total_profit, 2),
            "avg_profit_per_farmer": round(individual_avg_profit, 2),
            "avg_cost_per_farmer": round(individual_total_cost / farmer_count, 2),
        },
        "consolidated_scenario": {
            "total_revenue": round(bulk_price_revenue, 2),
            "total_cost": round(consolidated_total_cost, 2),
            "total_profit": round(consolidated_total_profit, 2),
            "avg_profit_per_farmer": round(consolidated_avg_profit, 2),
            "avg_cost_per_farmer": round(consolidated_cost_per_farmer, 2),
        },
        "improvement": {
            "profit_per_farmer_kes": round(improvement_per_farmer, 2),
            "profit_improvement_percent": round(improvement_percent, 1),
            "total_profit_improvement": round(consolidated_total_profit - individual_total_profit, 2),
            "cost_savings_per_farmer": round((individual_total_cost / farmer_count) - consolidated_cost_per_farmer, 2),
            "revenue_improvement_per_farmer": round((bulk_price_revenue / farmer_count) - (individual_total_revenue / farmer_count), 2),
        },
    }


def generate_negotiation_package(
    produce_type: str,
    individual_price: float,
    total_quantity_kg: float,
    farmer_count: int,
    market_name: str
) -> Dict:
    """
    Generate complete negotiation package with all leverage points.
    
    Args:
        produce_type: Type of produce
        individual_price: Current individual market price
        total_quantity_kg: Total consolidated quantity
        farmer_count: Number of farmers
        market_name: Target market name
        
    Returns:
        Complete negotiation package
    """
    bulk_pricing = calculate_bulk_pricing(individual_price, total_quantity_kg, produce_type)
    leverage = calculate_negotiation_leverage(total_quantity_kg, farmer_count, produce_type)
    
    sacks = round(total_quantity_kg / 90, 1)
    
    package = {
        "produce": produce_type,
        "market": market_name,
        "farmer_group": {
            "farmer_count": farmer_count,
            "total_quantity_kg": total_quantity_kg,
            "total_quantity_sacks": sacks,
        },
        "pricing": {
            "individual_price_per_kg": round(individual_price, 2),
            "proposed_bulk_price_per_kg": bulk_pricing["negotiated_price_per_kg"],
            "price_premium_percent": bulk_pricing["price_premium_percent"],
            "total_additional_revenue": bulk_pricing["total_additional_revenue"],
        },
        "leverage_points": leverage,
        "talking_points": [
            f"We represent {farmer_count} farmers with {sacks} sacks of {produce_type}",
            f"We can guarantee {sacks} sacks every {get_frequency_string(farmer_count)}",
            f"Single delivery point, organized loading, standard quality across all units",
            f"Premium price justified by volume, consistency, and quality assurance",
        ],
    }
    
    return package


def get_frequency_string(farmer_count: int) -> str:
    """
    Get frequency description based on farmer count.
    
    Args:
        farmer_count: Number of farmers in group
        
    Returns:
        Frequency description
    """
    if farmer_count < 5:
        return "2-3 weeks"
    elif farmer_count < 10:
        return "weekly"
    elif farmer_count < 20:
        return "twice weekly"
    else:
        return "multiple times per week"


def compare_selling_scenarios(
    produce: str,
    quantity_kg: float,
    individual_price: float,
    transport_cost_individual: float,
    transport_cost_consolidated: float,
    farmers_in_group: int
) -> Dict:
    """
    Compare all selling scenarios: individual, small group, large group.
    
    Args:
        produce: Produce type
        quantity_kg: Individual farmer quantity
        individual_price: Market price per kg
        transport_cost_individual: Individual transport cost
        transport_cost_consolidated: Consolidated transport cost per farmer
        farmers_in_group: How many farmers in consolidated group
        
    Returns:
        Comparison of scenarios
    """
    # Scenario 1: Individual sale
    individual_revenue = quantity_kg * individual_price
    individual_profit = individual_revenue - transport_cost_individual
    
    # Scenario 2: Small group (3-5 farmers)
    small_group_pricing = calculate_bulk_pricing(individual_price, quantity_kg * 3, produce)
    small_group_revenue_per_farmer = quantity_kg * small_group_pricing["negotiated_price_per_kg"]
    small_group_profit = small_group_revenue_per_farmer - transport_cost_consolidated
    
    # Scenario 3: Large group (8+ farmers)
    large_group_pricing = calculate_bulk_pricing(individual_price, quantity_kg * 10, produce)
    large_group_revenue_per_farmer = quantity_kg * large_group_pricing["negotiated_price_per_kg"]
    large_group_profit = large_group_revenue_per_farmer - transport_cost_consolidated
    
    # Actual scenario (based on farmers_in_group)
    actual_pricing = calculate_bulk_pricing(individual_price, quantity_kg * farmers_in_group, produce)
    actual_revenue = quantity_kg * actual_pricing["negotiated_price_per_kg"]
    actual_profit = actual_revenue - transport_cost_consolidated
    
    return {
        "individual": {
            "price_per_kg": round(individual_price, 2),
            "total_revenue": round(individual_revenue, 2),
            "transport_cost": round(transport_cost_individual, 2),
            "net_profit": round(individual_profit, 2),
            "profit_margin_percent": round((individual_profit / individual_revenue * 100) if individual_revenue > 0 else 0, 1),
        },
        "small_group_3_farmers": {
            "price_per_kg": round(small_group_pricing["negotiated_price_per_kg"], 2),
            "total_revenue": round(small_group_revenue_per_farmer, 2),
            "transport_cost": round(transport_cost_consolidated, 2),
            "net_profit": round(small_group_profit, 2),
            "profit_margin_percent": round((small_group_profit / small_group_revenue_per_farmer * 100) if small_group_revenue_per_farmer > 0 else 0, 1),
            "improvement_vs_individual_kes": round(small_group_profit - individual_profit, 2),
            "improvement_vs_individual_percent": round(((small_group_profit - individual_profit) / individual_profit * 100) if individual_profit > 0 else 0, 1),
        },
        "large_group_10_farmers": {
            "price_per_kg": round(large_group_pricing["negotiated_price_per_kg"], 2),
            "total_revenue": round(large_group_revenue_per_farmer, 2),
            "transport_cost": round(transport_cost_consolidated, 2),
            "net_profit": round(large_group_profit, 2),
            "profit_margin_percent": round((large_group_profit / large_group_revenue_per_farmer * 100) if large_group_revenue_per_farmer > 0 else 0, 1),
            "improvement_vs_individual_kes": round(large_group_profit - individual_profit, 2),
            "improvement_vs_individual_percent": round(((large_group_profit - individual_profit) / individual_profit * 100) if individual_profit > 0 else 0, 1),
        },
        "your_group": {
            "farmers_count": farmers_in_group,
            "price_per_kg": round(actual_pricing["negotiated_price_per_kg"], 2),
            "total_revenue": round(actual_revenue, 2),
            "transport_cost": round(transport_cost_consolidated, 2),
            "net_profit": round(actual_profit, 2),
            "profit_margin_percent": round((actual_profit / actual_revenue * 100) if actual_revenue > 0 else 0, 1),
            "improvement_vs_individual_kes": round(actual_profit - individual_profit, 2),
            "improvement_vs_individual_percent": round(((actual_profit - individual_profit) / individual_profit * 100) if individual_profit > 0 else 0, 1),
        },
    }
