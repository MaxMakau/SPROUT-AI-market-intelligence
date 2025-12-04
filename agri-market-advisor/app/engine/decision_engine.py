"""
Decision engine - core orchestrator for market recommendations.
Integrates all services to provide best market recommendation.
"""

from typing import Dict, List, Optional
from app.services.market_forecast import MarketForecastService
from app.services.profit_engine import ProfitEngine
from app.services.storage_engine import StorageEngine
from app.utils.transport_cost import calculate_transport_cost
from app.utils.helpers import calculate_transport_time_hours
from app.utils.constants import MARKET_LOCATIONS


class DecisionEngine:
    """
    Core orchestrator for market recommendations.
    Combines forecasting, profit calculation, and risk assessment.
    """
    
    def __init__(self):
        """Initialize decision engine with all services."""
        self.market_forecast = MarketForecastService()
        self.profit_engine = ProfitEngine()
        self.storage_engine = StorageEngine()
    
    def get_recommendation(self, input_data: dict) -> dict:
        """
        Get comprehensive market recommendation.
        
        Args:
            input_data: Dictionary with keys:
                - produce: str
                - quantity: float
                - location: str
                - transport_mode: str
                - has_storage: bool
                - moisture_level: Optional[float]
                - produce_grade: Optional[str]
                
        Returns:
            Dictionary with recommendation details
        """
        # Extract input
        produce = input_data["produce"]
        quantity = input_data["quantity"]
        location = input_data["location"]
        transport_mode = input_data["transport_mode"]
        has_storage = input_data["has_storage"]
        moisture_level = input_data.get("moisture_level")
        produce_grade = input_data.get("produce_grade", "B")
        
        # Step 1: Forecast prices for all markets
        price_forecasts = self.market_forecast.forecast_all_markets(
            produce, quantity, location, transport_mode, has_storage
        )
        
        # Step 2: Calculate profit for each market
        market_profits = {}
        market_details = {}
        
        for market in MARKET_LOCATIONS:
            predicted_price = price_forecasts[market]
            
            # Get transport cost
            transport_info = calculate_transport_cost(
                location, market, transport_mode, quantity
            )
            transport_cost = transport_info["total_cost"]
            distance = transport_info["distance_km"]
            
            # Calculate transport time
            transport_time = calculate_transport_time_hours(distance, transport_mode)
            
            # Calculate spoilage risk
            spoilage_risk = self.storage_engine.calculate_spoilage_risk(
                produce, transport_time, has_storage
            )
            
            # Calculate spoilage loss value
            spoilage_loss = self.storage_engine.calculate_spoilage_loss_value(
                quantity, predicted_price, spoilage_risk
            )
            
            # Calculate production cost
            production_cost = self.profit_engine.calculate_production_cost(
                quantity, produce
            )
            
            # Calculate storage cost
            storage_cost = self.profit_engine.calculate_storage_cost(
                quantity, has_storage, transport_time
            )
            
            # Calculate net profit
            profit_info = self.profit_engine.calculate_net_profit(
                quantity, predicted_price, transport_cost,
                production_cost, storage_cost, spoilage_loss
            )
            
            market_profits[market] = profit_info
            market_details[market] = {
                "predicted_price": predicted_price,
                "transport_cost": transport_cost,
                "distance_km": distance,
                "transport_time_hours": transport_time,
                "spoilage_risk": spoilage_risk,
                "spoilage_loss": spoilage_loss
            }
        
        # Step 3: Find best market
        best_market, best_profit = self.profit_engine.compare_profits(market_profits)
        
        # Step 4: Generate recommendation reason
        recommendation_reason = self._generate_recommendation_reason(
            best_market, market_details[best_market], produce, quantity
        )
        
        # Step 5: Create detailed response
        breakdown = []
        for market in MARKET_LOCATIONS:
            breakdown.append({
                "market": market,
                "predicted_price": round(market_details[market]["predicted_price"], 2),
                "transport_cost": round(market_details[market]["transport_cost"], 2),
                "spoilage_risk": market_details[market]["spoilage_risk"],
                "expected_revenue": round(market_profits[market]["revenue"], 2),
                "net_profit": round(market_profits[market]["net_profit"], 2)
            })
        
        # Sort breakdown by net profit
        breakdown = sorted(breakdown, key=lambda x: x["net_profit"], reverse=True)
        
        response = {
            "best_market": best_market,
            "expected_price": round(market_details[best_market]["predicted_price"], 2),
            "transport_cost": round(market_details[best_market]["transport_cost"], 2),
            "spoilage_risk": market_details[best_market]["spoilage_risk"],
            "expected_revenue": round(best_profit["revenue"], 2),
            "net_profit": round(best_profit["net_profit"], 2),
            "profit_margin_percent": best_profit["profit_margin_percent"],
            "breakdown": breakdown,
            "recommendation_reason": recommendation_reason,
            "additional_info": {
                "produce": produce,
                "quantity": quantity,
                "quantity_unit": "kg",
                "location": location,
                "transport_mode": transport_mode,
                "has_storage": has_storage,
                "distance_to_best_market_km": market_details[best_market]["distance_km"],
                "estimated_travel_time_hours": market_details[best_market]["transport_time_hours"],
                "moisture_level": moisture_level,
                "produce_grade": produce_grade
            }
        }
        
        return response
    
    def _generate_recommendation_reason(self,
                                       best_market: str,
                                       market_info: dict,
                                       produce: str,
                                       quantity: float) -> str:
        """
        Generate human-readable recommendation reason.
        
        Args:
            best_market: Best market name
            market_info: Market information
            produce: Type of produce
            quantity: Quantity
            
        Returns:
            Recommendation reason text
        """
        price = market_info["predicted_price"]
        spoilage_risk = market_info["spoilage_risk"]
        distance = market_info["distance_km"]
        
        reasons = []
        
        # Price reason
        reasons.append(f"highest expected price of KES {price:.2f}/kg")
        
        # Risk reason
        if spoilage_risk < 10:
            reasons.append("low spoilage risk")
        elif spoilage_risk < 20:
            reasons.append("manageable spoilage risk")
        else:
            reasons.append("acceptable for risk tolerance")
        
        # Distance reason
        if distance < 100:
            reasons.append("minimal transport distance")
        elif distance < 200:
            reasons.append("reasonable transport distance")
        else:
            reasons.append("accessible despite distance")
        
        reason_text = ". ".join([r[0].upper() + r[1:] for r in reasons])
        
        return (
            f"{best_market} offers the best opportunity for your {produce}. "
            f"{reason_text}. Recommended action: Prepare produce for immediate transport."
        )
    
    def get_detailed_market_analysis(self, input_data: dict) -> dict:
        """
        Get detailed analysis for market comparison.
        
        Args:
            input_data: Farmer input data
            
        Returns:
            Detailed market analysis
        """
        recommendation = self.get_recommendation(input_data)
        
        # Additional analysis
        produce = input_data["produce"]
        shelf_life = self.storage_engine.get_produce_shelf_life(produce)
        moisture_impact = self.storage_engine.estimate_moisture_impact(
            produce, input_data.get("moisture_level")
        )
        
        return {
            **recommendation,
            "shelf_life_days": shelf_life.get("days", 14),
            "optimal_storage_temperature": shelf_life.get("optimal_temp", 15),
            "optimal_storage_humidity": shelf_life.get("optimal_humidity", 80),
            "moisture_analysis": moisture_impact,
            "storage_recommendation": self.storage_engine.get_storage_recommendation(
                produce,
                recommendation["additional_info"]["estimated_travel_time_hours"],
                input_data["has_storage"]
            )
        }
    
    def validate_input(self, input_data: dict) -> tuple:
        """
        Validate input data.
        
        Args:
            input_data: Input dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["produce", "quantity", "location", "transport_mode", "has_storage"]
        
        for field in required_fields:
            if field not in input_data:
                return False, f"Missing required field: {field}"
        
        if input_data["quantity"] <= 0:
            return False, "Quantity must be positive"
        
        if input_data["transport_mode"] not in ["motorbike", "pickup", "lorry"]:
            return False, "Invalid transport mode"
        
        if not isinstance(input_data["has_storage"], bool):
            return False, "has_storage must be boolean"
        
        return True, "Valid"
