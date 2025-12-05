"""
Pydantic schemas for clustering, routing, and shipment APIs.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class FarmerClusterData(BaseModel):
    """Farmer data for clustering."""
    farmer_id: str
    location_name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    produce: str
    quantity_kg: float = Field(..., gt=0)
    cost_individual_kes: float = Field(..., ge=0)


class CreateClusterRequest(BaseModel):
    """Request to create a new cluster."""
    cluster_name: str = Field(..., description="Human-readable cluster name")
    region: str = Field(..., description="Region name")
    produce: str = Field(..., description="Produce type")
    target_market: str = Field(..., description="Target market location")
    pickup_date: datetime = Field(..., description="Scheduled pickup date")


class CreateClusterResponse(BaseModel):
    """Response when cluster created."""
    cluster_id: str
    cluster_name: str
    region: str
    produce: str
    target_market: str
    status: str = "forming"
    quality_score: float
    members_count: int = 0
    total_quantity_kg: float = 0


class AddFarmerToClusterRequest(BaseModel):
    """Request to add farmer to cluster."""
    cluster_id: str
    farmer_id: str
    location_name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    produce: str
    quantity_kg: float = Field(..., gt=0)
    cost_individual_kes: float = Field(..., ge=0)


class RemoveFarmerRequest(BaseModel):
    """Request to remove farmer from cluster."""
    cluster_id: str
    farmer_id: str
    reason: str = Field(default="user_request")


class CommitFarmerRequest(BaseModel):
    """Request to commit farmer to cluster."""
    cluster_id: str
    farmer_id: str


class LockClusterRequest(BaseModel):
    """Request to lock cluster (no more changes)."""
    cluster_id: str


class WaypointResponse(BaseModel):
    """Single waypoint in a route."""
    order: int
    location: str
    cumulative_distance_km: float
    estimated_arrival_minutes: int


class RouteResponse(BaseModel):
    """Optimized route response."""
    route_id: str
    total_distance_km: float
    total_stops: int
    vehicle_type: str
    time: Dict = Field(..., description="Time breakdown")
    cost: Dict = Field(..., description="Cost breakdown")
    cost_per_farmer_kes: float
    waypoints: List[WaypointResponse]


class BulkPricingResponse(BaseModel):
    """Bulk pricing information."""
    base_price_per_kg: float
    total_quantity_kg: float
    negotiated_price_per_kg: float
    price_premium_percent: float
    additional_revenue_per_kg: float
    total_additional_revenue: float


class NegotiationLeverageResponse(BaseModel):
    """Negotiation leverage points."""
    volume_message: str
    consistency_message: str
    quality_message: str
    reliability_message: str
    logistics_message: str
    market_category: str
    negotiation_power: str


class ClusterMemberResponse(BaseModel):
    """Member of a cluster."""
    farmer_id: str
    location_name: str
    quantity_kg: float
    cost_individual_kes: float
    status: str


class ClusterDetailsResponse(BaseModel):
    """Detailed cluster information."""
    cluster_id: str
    cluster_name: str
    region: str
    produce: str
    target_market: str
    status: str
    quality_score: float
    members_count: int
    total_quantity_kg: float
    total_quantity_sacks: float
    cost_per_farmer_kes: float
    savings_percent: float
    members: List[ClusterMemberResponse]
    pickup_date: Optional[datetime]
    vehicle_assigned: Optional[str]


class ClusterListResponse(BaseModel):
    """List of clusters."""
    total_clusters: int
    clusters: List[ClusterDetailsResponse]


class FindClustersRequest(BaseModel):
    """Request to find available clusters to join."""
    produce: str = Field(..., description="Produce type")
    target_market: str = Field(..., description="Target market")
    region: Optional[str] = Field(None, description="Region (optional filter)")


class AvailableClustersResponse(BaseModel):
    """List of available clusters to join."""
    total_available: int
    clusters: List[Dict]


class GenerateRouteRequest(BaseModel):
    """Request to generate optimized route."""
    cluster_id: str
    start_market_latitude: float = Field(..., ge=-90, le=90)
    start_market_longitude: float = Field(..., ge=-180, le=180)
    start_market_name: str


class GenerateShipmentRequest(BaseModel):
    """Request to generate shipment from cluster."""
    cluster_id: str
    vehicle_type: str = Field(..., description="motorbike, pickup, or lorry")
    route_id: str
    estimated_cost_kes: float = Field(..., ge=0)


class ShipmentResponse(BaseModel):
    """Shipment information."""
    shipment_id: str
    cluster_id: str
    vehicle_type: str
    route_id: str
    total_quantity_kg: float
    total_quantity_sacks: float
    estimated_cost_kes: float
    cost_per_farmer_kes: float
    farmer_count: int
    status: str
    created_at: datetime


class ProfitComparisonResponse(BaseModel):
    """Comparison of profit scenarios."""
    individual_scenario: Dict
    consolidated_scenario: Dict
    improvement: Dict


class ClusteringOpportunityResponse(BaseModel):
    """Clustering opportunity identified."""
    opportunity_id: str
    description: str
    potential_members: int
    potential_savings_kes: float
    potential_savings_percent: float
    recommended_action: str


class AvailableClustersForJoiningResponse(BaseModel):
    """Available clusters that farmer can join."""
    total_available: int
    clusters: List[Dict] = Field(..., description="List of available clusters with details")

    class Config:
        schema_extra = {
            "example": {
                "total_available": 2,
                "clusters": [
                    {
                        "cluster_id": "cluster_abc123",
                        "cluster_name": "Western Region Maize Group",
                        "region": "Kisii",
                        "produce": "maize",
                        "target_market": "Nairobi Central Market",
                        "members_count": 5,
                        "total_quantity_kg": 450,
                        "cost_per_farmer_kes": 650,
                        "savings_percent": 35.5,
                        "pickup_date": "2024-12-15T08:00:00",
                        "status": "forming",
                        "quality_score": 0.78,
                    }
                ]
            }
        }
