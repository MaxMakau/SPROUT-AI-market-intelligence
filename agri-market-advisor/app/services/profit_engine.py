"""
Profit calculation engine.
Computes expected revenue and net profit per market.
"""

from typing import Dict, List, Tuple
from app.utils.transport_cost import calculate_transport_cost


class ProfitEngine:
    """
    Engine for calculating expected profit per market.
    """
    
    def __init__(self):
        """Initialize profit engine."""
        self.base_cost_per_kg = 5.0  # Mock production cost
    
    def calculate_revenue(self, quantity: float, price_per_unit: float) -> float:
        """
        Calculate total expected revenue.
        
        Args:
            quantity: Quantity in kg
            price_per_unit: Price per kg in KES
            
        Returns:
            Total revenue in KES
        """
        return quantity * price_per_unit
    
    def calculate_production_cost(self, quantity: float, produce: str) -> float:
        """
        Calculate production cost for produce.
        
        Args:
            quantity: Quantity in kg
            produce: Type of produce
            
        Returns:
            Production cost in KES
        """
        # Mock cost calculation based on produce type
        produce_costs = {
            "maize": 4.0,
            "beans": 8.0,
            "tomato": 10.0,
            "potato": 6.0,
            "onion": 7.0,
            "milk": 25.0,
            "eggs": 300.0,  # per crate
            "chicken": 150.0,
        }
        
        cost_per_kg = produce_costs.get(produce.lower(), 5.0)
        return quantity * cost_per_kg
    
    def calculate_storage_cost(self,
                              quantity: float,
                              has_storage: bool,
                              transport_time_hours: float) -> float:
        """
        Calculate storage costs.
        
        Args:
            quantity: Quantity in kg
            has_storage: Whether farmer has storage
            transport_time_hours: Transport time in hours
            
        Returns:
            Storage cost in KES
        """
        if has_storage:
            # Reduce spoilage loss cost
            return quantity * 0.5  # 0.5 KES/kg for storage maintenance
        else:
            # Cost of spoilage due to lack of storage
            spoilage_loss_rate = (transport_time_hours / 24) * 0.05  # 5% loss per day
            return quantity * spoilage_loss_rate * 10  # Estimated loss value
    
    def calculate_marketing_cost(self, revenue: float) -> float:
        """
        Calculate marketing and transaction costs.
        
        Args:
            revenue: Expected revenue in KES
            
        Returns:
            Marketing cost in KES
        """
        # 5% of revenue for marketing, taxes, and transaction fees
        return revenue * 0.05
    
    def calculate_net_profit(self,
                            quantity: float,
                            predicted_price: float,
                            transport_cost: float,
                            production_cost: float,
                            storage_cost: float,
                            spoilage_loss: float) -> dict:
        """
        Calculate total net profit.
        
        Args:
            quantity: Quantity in kg
            predicted_price: Predicted price per kg
            transport_cost: Transport cost
            production_cost: Production cost
            storage_cost: Storage cost
            spoilage_loss: Value lost to spoilage
            
        Returns:
            Dictionary with profit breakdown
        """
        revenue = self.calculate_revenue(quantity, predicted_price)
        marketing_cost = self.calculate_marketing_cost(revenue)
        
        total_costs = (
            production_cost + 
            transport_cost + 
            storage_cost + 
            marketing_cost + 
            spoilage_loss
        )
        
        net_profit = revenue - total_costs
        profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        return {
            "revenue": round(revenue, 2),
            "production_cost": round(production_cost, 2),
            "transport_cost": round(transport_cost, 2),
            "storage_cost": round(storage_cost, 2),
            "marketing_cost": round(marketing_cost, 2),
            "spoilage_loss": round(spoilage_loss, 2),
            "total_costs": round(total_costs, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin_percent": round(profit_margin, 2)
        }
    
    def compare_profits(self, market_profits: Dict[str, dict]) -> Tuple[str, dict]:
        """
        Compare profits across markets and find best.
        
        Args:
            market_profits: Dictionary mapping markets to profit info
            
        Returns:
            Tuple of (best_market, best_profit_info)
        """
        if not market_profits:
            return None, None
        
        best_market = max(
            market_profits.keys(),
            key=lambda m: market_profits[m]["net_profit"]
        )
        
        return best_market, market_profits[best_market]
    
    def generate_profit_ranking(self, market_profits: Dict[str, dict]) -> List[dict]:
        """
        Generate ranking of markets by profit.
        
        Args:
            market_profits: Dictionary mapping markets to profit info
            
        Returns:
            List of markets ranked by net profit (descending)
        """
        ranked = sorted(
            [{"market": m, **p} for m, p in market_profits.items()],
            key=lambda x: x["net_profit"],
            reverse=True
        )
        
        for i, item in enumerate(ranked, 1):
            item["rank"] = i
        
        return ranked
