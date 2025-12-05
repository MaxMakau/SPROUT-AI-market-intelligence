"""
Cluster coordination service for managing cluster lifecycle and membership.
Handles farmer enrollment, cluster state management, and shipment generation.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import uuid


class ClusterStatus(str, Enum):
    """Status of a cluster."""
    FORMING = "forming"          # Accepting members
    LOCKED = "locked"             # No more changes, scheduled for pickup
    IN_TRANSIT = "in_transit"     # Vehicle picked up and on route
    DELIVERED = "delivered"       # Delivered to market
    CANCELLED = "cancelled"       # Cluster cancelled


class FarmerStatus(str, Enum):
    """Status of farmer in cluster."""
    PENDING = "pending"           # Initial state
    COMMITTED = "committed"       # Confirmed participation
    COLLECTED = "collected"       # Picked up by vehicle
    FAILED = "failed"             # Could not collect (e.g., quantity changed)
    CANCELLED = "cancelled"       # Withdrew from cluster


@dataclass
class ClusterConfig:
    """Configuration for cluster formation."""
    max_radius_km: float = 15.0
    min_cluster_size: int = 3
    min_quality_score: float = 0.5
    min_savings_percent: float = 15.0
    formation_window_days: int = 5
    vehicle_types: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.vehicle_types is None:
            self.vehicle_types = {
                "motorbike": {"capacity_sacks": 3, "cost_per_sack": 1000},
                "pickup": {"capacity_sacks": 20, "cost_per_sack": 700},
                "lorry": {"capacity_sacks": 40, "cost_per_sack": 400},
            }


class ClusterCoordinator:
    """Manages cluster formation, membership, and lifecycle."""
    
    def __init__(self, config: ClusterConfig = None):
        """
        Initialize cluster coordinator.
        
        Args:
            config: Cluster configuration
        """
        self.config = config or ClusterConfig()
        self.clusters: Dict[str, Dict] = {}
        self.farmers: Dict[str, Dict] = {}
    
    def create_cluster(
        self,
        cluster_name: str,
        region: str,
        produce: str,
        target_market: str,
        pickup_date: datetime,
        quality_score: float = 0.7
    ) -> Dict:
        """
        Create a new forming cluster.
        
        Args:
            cluster_name: Human-readable cluster name
            region: Region name
            produce: Produce type
            target_market: Target market location
            pickup_date: Scheduled pickup date
            quality_score: Initial quality score
            
        Returns:
            Cluster information
        """
        cluster_id = f"cluster_{str(uuid.uuid4())[:8]}"
        
        cluster = {
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "region": region,
            "produce": produce,
            "target_market": target_market,
            "status": ClusterStatus.FORMING,
            "quality_score": quality_score,
            "pickup_date": pickup_date,
            "members": [],
            "total_quantity_kg": 0,
            "vehicle_assigned": None,
            "route_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "savings_percent": 0,
            "cost_per_farmer": 0,
        }
        
        self.clusters[cluster_id] = cluster
        return cluster
    
    def add_farmer_to_cluster(
        self,
        cluster_id: str,
        farmer_id: str,
        location_name: str,
        location: Tuple[float, float],
        quantity_kg: float,
        cost_individual: float
    ) -> Dict:
        """
        Add farmer to a cluster.
        
        Args:
            cluster_id: Cluster to join
            farmer_id: Farmer identifier
            location_name: Location name
            location: (latitude, longitude)
            quantity_kg: Quantity in kg
            cost_individual: Cost if shipping individually
            
        Returns:
            Updated cluster information
        """
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster = self.clusters[cluster_id]
        
        if cluster["status"] != ClusterStatus.FORMING:
            raise ValueError(f"Cluster {cluster_id} is not accepting new members (status: {cluster['status']})")
        
        # Create farmer member record
        member = {
            "farmer_id": farmer_id,
            "location_name": location_name,
            "location": location,
            "quantity_kg": quantity_kg,
            "cost_individual": cost_individual,
            "status": FarmerStatus.PENDING,
            "joined_at": datetime.now(),
        }
        
        # Add to cluster
        cluster["members"].append(member)
        cluster["total_quantity_kg"] += quantity_kg
        cluster["updated_at"] = datetime.now()
        
        # Recalculate cluster metrics
        self._recalculate_cluster_metrics(cluster_id)
        
        return cluster
    
    def remove_farmer_from_cluster(
        self,
        cluster_id: str,
        farmer_id: str,
        reason: str = "user_request"
    ) -> Dict:
        """
        Remove farmer from a cluster.
        
        Args:
            cluster_id: Cluster to leave
            farmer_id: Farmer to remove
            reason: Reason for removal
            
        Returns:
            Updated cluster information
        """
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster = self.clusters[cluster_id]
        
        # Find and remove farmer
        for i, member in enumerate(cluster["members"]):
            if member["farmer_id"] == farmer_id:
                removed = cluster["members"].pop(i)
                cluster["total_quantity_kg"] -= removed["quantity_kg"]
                cluster["updated_at"] = datetime.now()
                break
        else:
            raise ValueError(f"Farmer {farmer_id} not found in cluster")
        
        # Recalculate metrics
        self._recalculate_cluster_metrics(cluster_id)
        
        return cluster
    
    def commit_farmer(
        self,
        cluster_id: str,
        farmer_id: str
    ) -> Dict:
        """
        Mark farmer as committed (confirmed participation).
        
        Args:
            cluster_id: Cluster ID
            farmer_id: Farmer ID
            
        Returns:
            Updated member information
        """
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster = self.clusters[cluster_id]
        
        for member in cluster["members"]:
            if member["farmer_id"] == farmer_id:
                member["status"] = FarmerStatus.COMMITTED
                member["committed_at"] = datetime.now()
                cluster["updated_at"] = datetime.now()
                return member
        
        raise ValueError(f"Farmer {farmer_id} not found in cluster")
    
    def lock_cluster(
        self,
        cluster_id: str
    ) -> Dict:
        """
        Lock cluster - no more member changes allowed.
        Cluster is scheduled for pickup.
        
        Args:
            cluster_id: Cluster to lock
            
        Returns:
            Updated cluster information
        """
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster = self.clusters[cluster_id]
        
        # Validate cluster is viable
        if len(cluster["members"]) < self.config.min_cluster_size:
            raise ValueError(
                f"Cluster has {len(cluster['members'])} members, "
                f"minimum {self.config.min_cluster_size} required"
            )
        
        if cluster["quality_score"] < self.config.min_quality_score:
            raise ValueError(
                f"Cluster quality score {cluster['quality_score']} "
                f"below minimum {self.config.min_quality_score}"
            )
        
        # Lock it
        cluster["status"] = ClusterStatus.LOCKED
        cluster["locked_at"] = datetime.now()
        cluster["updated_at"] = datetime.now()
        
        # Mark all members as committed
        for member in cluster["members"]:
            if member["status"] == FarmerStatus.PENDING:
                member["status"] = FarmerStatus.COMMITTED
        
        return cluster
    
    def generate_shipment(
        self,
        cluster_id: str,
        vehicle_type: str,
        route_id: str,
        estimated_cost: float
    ) -> Dict:
        """
        Generate shipment from locked cluster.
        
        Args:
            cluster_id: Cluster to ship
            vehicle_type: Vehicle type (motorbike, pickup, lorry)
            route_id: Route ID
            estimated_cost: Estimated total cost
            
        Returns:
            Shipment information
        """
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster = self.clusters[cluster_id]
        
        if cluster["status"] != ClusterStatus.LOCKED:
            raise ValueError(f"Cluster must be locked before generating shipment")
        
        shipment_id = f"shipment_{str(uuid.uuid4())[:8]}"
        
        # Calculate cost per farmer
        cost_per_farmer = estimated_cost / len(cluster["members"])
        
        shipment = {
            "shipment_id": shipment_id,
            "cluster_id": cluster_id,
            "vehicle_type": vehicle_type,
            "route_id": route_id,
            "total_quantity_kg": cluster["total_quantity_kg"],
            "total_quantity_sacks": round(cluster["total_quantity_kg"] / 90, 1),
            "estimated_cost": estimated_cost,
            "cost_per_farmer": cost_per_farmer,
            "farmer_count": len(cluster["members"]),
            "status": "scheduled",
            "created_at": datetime.now(),
        }
        
        # Update cluster
        cluster["vehicle_assigned"] = vehicle_type
        cluster["route_id"] = route_id
        cluster["status"] = ClusterStatus.IN_TRANSIT
        cluster["updated_at"] = datetime.now()
        
        return shipment
    
    def _recalculate_cluster_metrics(self, cluster_id: str):
        """
        Recalculate cluster quality score and cost metrics.
        
        Args:
            cluster_id: Cluster to recalculate
        """
        cluster = self.clusters[cluster_id]
        members = cluster["members"]
        
        if not members:
            cluster["quality_score"] = 0
            cluster["cost_per_farmer"] = 0
            cluster["savings_percent"] = 0
            return
        
        # Recalculate based on current members
        total_quantity = cluster["total_quantity_kg"]
        total_individual_cost = sum(m["cost_individual"] for m in members)
        
        # Estimate consolidated cost (rough estimate)
        total_sacks = total_quantity / 90
        if total_sacks <= 3:
            vehicle = "motorbike"
            cost_per_sack = 1000
        elif total_sacks <= 20:
            vehicle = "pickup"
            cost_per_sack = 700
        else:
            vehicle = "lorry"
            cost_per_sack = 400
        
        estimated_consolidated_cost = total_sacks * cost_per_sack
        cost_per_farmer = estimated_consolidated_cost / len(members)
        
        # Calculate savings
        savings_percent = ((total_individual_cost - estimated_consolidated_cost) / total_individual_cost * 100) if total_individual_cost > 0 else 0
        
        cluster["cost_per_farmer"] = round(cost_per_farmer, 2)
        cluster["savings_percent"] = round(savings_percent, 1)
    
    def get_cluster(self, cluster_id: str) -> Dict:
        """Get cluster information."""
        if cluster_id not in self.clusters:
            raise ValueError(f"Cluster {cluster_id} not found")
        return self.clusters[cluster_id]
    
    def get_active_clusters(self, region: str = None, produce: str = None) -> List[Dict]:
        """
        Get all active (forming) clusters.
        
        Args:
            region: Filter by region (optional)
            produce: Filter by produce type (optional)
            
        Returns:
            List of active clusters
        """
        active = [
            c for c in self.clusters.values()
            if c["status"] == ClusterStatus.FORMING
        ]
        
        if region:
            active = [c for c in active if c["region"].lower() == region.lower()]
        
        if produce:
            active = [c for c in active if c["produce"].lower() == produce.lower()]
        
        return sorted(active, key=lambda c: c["quality_score"], reverse=True)
    
    def get_farmer_clusters(self, farmer_id: str) -> List[Dict]:
        """
        Get all clusters a farmer is part of.
        
        Args:
            farmer_id: Farmer ID
            
        Returns:
            List of clusters containing this farmer
        """
        farmer_clusters = []
        
        for cluster in self.clusters.values():
            for member in cluster["members"]:
                if member["farmer_id"] == farmer_id:
                    farmer_clusters.append({
                        "cluster": cluster,
                        "member": member
                    })
                    break
        
        return farmer_clusters


def estimate_cluster_viability(
    farmers_data: List[Dict],
    target_market: str,
    min_farmers: int = 3
) -> Dict:
    """
    Estimate if a group of farmers can form a viable cluster.
    
    Args:
        farmers_data: List of farmer data dicts with location, quantity, produce
        target_market: Target market
        min_farmers: Minimum viable farmers
        
    Returns:
        Viability assessment
    """
    if len(farmers_data) < min_farmers:
        return {
            "viable": False,
            "reason": f"Need at least {min_farmers} farmers, have {len(farmers_data)}",
            "potential_savings": 0
        }
    
    # Check produce uniformity
    produces = [f.get("produce", "").lower() for f in farmers_data]
    if len(set(produces)) > 1:
        return {
            "viable": False,
            "reason": "Mixed produce types - recommend separate clusters",
            "potential_savings": 0
        }
    
    # Calculate potential savings
    total_quantity = sum(f.get("quantity_kg", 0) for f in farmers_data)
    total_individual_cost = sum(f.get("cost_individual", 0) for f in farmers_data)
    
    total_sacks = total_quantity / 90
    if total_sacks <= 3:
        consolidated_cost = total_sacks * 1000
    elif total_sacks <= 20:
        consolidated_cost = total_sacks * 700
    else:
        consolidated_cost = total_sacks * 400
    
    savings = total_individual_cost - consolidated_cost
    savings_percent = (savings / total_individual_cost * 100) if total_individual_cost > 0 else 0
    
    return {
        "viable": savings_percent >= 15,
        "reason": f"Potential savings: {savings_percent:.1f}%",
        "potential_savings_kes": round(savings, 2),
        "potential_savings_percent": round(savings_percent, 1),
        "total_quantity_kg": total_quantity,
        "total_sacks": round(total_sacks, 1),
        "farmers_count": len(farmers_data),
    }
