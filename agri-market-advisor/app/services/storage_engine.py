"""
Storage and spoilage risk engine.
Estimates spoilage risk based on produce type and conditions.
"""

from typing import Dict
from app.utils.constants import SPOILAGE_RISK_MULTIPLIERS, STORAGE_RISK_REDUCTION


class StorageEngine:
    """
    Engine for calculating spoilage risk and storage impact.
    """
    
    def __init__(self):
        """Initialize storage engine."""
        self.base_risk_multipliers = SPOILAGE_RISK_MULTIPLIERS
        self.storage_reduction = STORAGE_RISK_REDUCTION
    
    def calculate_spoilage_risk(self,
                               produce: str,
                               transport_time_hours: float,
                               has_storage: bool,
                               temperature_factor: float = 1.0) -> float:
        """
        Calculate spoilage risk percentage.
        
        Args:
            produce: Type of produce
            transport_time_hours: Transport time in hours
            has_storage: Whether farmer has storage facility
            temperature_factor: Temperature stress factor (1.0 = normal)
            
        Returns:
            Spoilage risk as percentage (0-100)
        """
        # Get base risk multiplier for produce
        base_multiplier = self.base_risk_multipliers.get(produce.lower(), 2.0)
        
        # Calculate risk based on transport time
        days_in_transit = transport_time_hours / 24
        base_risk = base_multiplier * days_in_transit
        
        # Apply temperature stress
        risk_with_temp = base_risk * temperature_factor
        
        # Apply storage reduction
        if has_storage:
            final_risk = max(risk_with_temp - self.storage_reduction, 0)
        else:
            final_risk = risk_with_temp
        
        # Cap at 100%
        return min(round(final_risk, 1), 100.0)
    
    def calculate_spoilage_loss_value(self,
                                     quantity: float,
                                     price_per_unit: float,
                                     spoilage_risk_percent: float) -> float:
        """
        Calculate monetary value of spoilage loss.
        
        Args:
            quantity: Quantity in kg
            price_per_unit: Price per kg
            spoilage_risk_percent: Spoilage risk percentage
            
        Returns:
            Estimated loss value in KES
        """
        quantity_at_risk = quantity * (spoilage_risk_percent / 100)
        loss_value = quantity_at_risk * price_per_unit
        return round(loss_value, 2)
    
    def get_produce_shelf_life(self, produce: str) -> dict:
        """
        Get estimated shelf life for produce type.
        
        Args:
            produce: Type of produce
            
        Returns:
            Dictionary with shelf life information
        """
        shelf_lives = {
            # Perishable
            "tomato": {"days": 5, "optimal_temp": 20, "optimal_humidity": 85},
            "pepper": {"days": 7, "optimal_temp": 8, "optimal_humidity": 90},
            "onion": {"days": 30, "optimal_temp": 10, "optimal_humidity": 75},
            "spinach": {"days": 3, "optimal_temp": 4, "optimal_humidity": 95},
            "lettuce": {"days": 5, "optimal_temp": 4, "optimal_humidity": 95},
            "banana": {"days": 10, "optimal_temp": 13, "optimal_humidity": 85},
            "milk": {"days": 2, "optimal_temp": 4, "optimal_humidity": 70},
            "fish": {"days": 1, "optimal_temp": 0, "optimal_humidity": 90},
            # Semi-perishable
            "potato": {"days": 60, "optimal_temp": 10, "optimal_humidity": 85},
            "carrot": {"days": 30, "optimal_temp": 4, "optimal_humidity": 90},
            # Non-perishable
            "maize": {"days": 180, "optimal_temp": 20, "optimal_humidity": 65},
            "beans": {"days": 180, "optimal_temp": 20, "optimal_humidity": 65},
            "rice": {"days": 360, "optimal_temp": 20, "optimal_humidity": 60},
        }
        
        return shelf_lives.get(produce.lower(), {
            "days": 14,
            "optimal_temp": 15,
            "optimal_humidity": 80
        })
    
    def get_storage_recommendation(self,
                                  produce: str,
                                  transport_time_hours: float,
                                  has_storage: bool) -> str:
        """
        Get storage recommendation for produce.
        
        Args:
            produce: Type of produce
            transport_time_hours: Transport time in hours
            has_storage: Whether farmer has storage
            
        Returns:
            Recommendation text
        """
        shelf_life = self.get_produce_shelf_life(produce)
        days_in_transit = transport_time_hours / 24
        
        if not has_storage:
            if days_in_transit > shelf_life.get("days", 14):
                return f"URGENT: Transport time ({int(days_in_transit)} days) exceeds shelf life. Consider storage or expedited transport."
            else:
                return f"Storage recommended to reduce spoilage risk and extend market window."
        else:
            return f"Storage facility available. Optimal storage temperature: {shelf_life['optimal_temp']}°C"
    
    def estimate_moisture_impact(self,
                                produce: str,
                                moisture_level: float) -> dict:
        """
        Estimate impact of moisture level on spoilage.
        
        Args:
            produce: Type of produce
            moisture_level: Current moisture level percentage
            
        Returns:
            Dictionary with moisture impact assessment
        """
        optimal_moisture = {
            "maize": 13.5,
            "rice": 14.0,
            "beans": 12.0,
            "wheat": 13.5,
            "sorghum": 12.0,
        }
        
        target = optimal_moisture.get(produce.lower(), 12.0)
        
        if moisture_level is None:
            return {
                "status": "unknown",
                "impact": "moisture data not provided",
                "risk_adjustment": 0.0
            }
        
        difference = abs(moisture_level - target)
        
        if difference < 1.0:
            status = "optimal"
            risk_adjustment = 0.0
        elif difference < 3.0:
            status = "acceptable"
            risk_adjustment = 5.0
        else:
            status = "suboptimal"
            risk_adjustment = 15.0
        
        return {
            "status": status,
            "optimal_moisture": target,
            "current_moisture": moisture_level,
            "difference": round(difference, 1),
            "risk_adjustment": risk_adjustment
        }
