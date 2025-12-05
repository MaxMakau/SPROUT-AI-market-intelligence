"""
Clustering and route optimization API endpoints.
Provides clustering formation, route optimization, and shipment management.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List
import uuid

from app.schemas.clustering_schema import (
    CreateClusterRequest, CreateClusterResponse,
    AddFarmerToClusterRequest, RemoveFarmerRequest,
    CommitFarmerRequest, LockClusterRequest,
    FindClustersRequest, AvailableClustersForJoiningResponse,
    GenerateRouteRequest, RouteResponse,
    GenerateShipmentRequest, ShipmentResponse,
    ClusterDetailsResponse, ClusterListResponse,
    ProfitComparisonResponse, BulkPricingResponse, NegotiationLeverageResponse
)
from app.services.clustering_engine import (
    find_clusters, Farmer, calculate_cluster_quality_score
)
from app.services.route_optimization_engine import (
    nearest_neighbor_route, Location, two_opt_improvement,
    generate_route_summary, estimate_pickup_time
)
from app.services.cluster_coordination_service import (
    ClusterCoordinator, ClusterConfig
)
from app.services.market_negotiation_engine import (
    calculate_bulk_pricing, calculate_negotiation_leverage,
    compare_selling_scenarios, calculate_profit_improvement
)

router = APIRouter(prefix="/api/clusters", tags=["Clustering"])
coordinator = ClusterCoordinator()

# ============================================================================
# CLUSTER MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/create", response_model=CreateClusterResponse)
async def create_cluster(request: CreateClusterRequest) -> dict:
    """
    Create a new cluster for farmer consolidation.
    
    Cluster starts in 'forming' state and accepts farmer members.
    
    Args:
        request: CreateClusterRequest with cluster details
        
    Returns:
        CreateClusterResponse with cluster information
    """
    try:
        cluster = coordinator.create_cluster(
            cluster_name=request.cluster_name,
            region=request.region,
            produce=request.produce,
            target_market=request.target_market,
            pickup_date=request.pickup_date,
            quality_score=0.7
        )
        
        return CreateClusterResponse(
            cluster_id=cluster["cluster_id"],
            cluster_name=cluster["cluster_name"],
            region=cluster["region"],
            produce=cluster["produce"],
            target_market=cluster["target_market"],
            status=cluster["status"].value,
            quality_score=cluster["quality_score"],
            members_count=0,
            total_quantity_kg=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating cluster: {str(e)}")


@router.post("/{cluster_id}/add-farmer")
async def add_farmer_to_cluster(cluster_id: str, request: AddFarmerToClusterRequest) -> dict:
    """
    Add a farmer to an existing cluster.
    
    Args:
        cluster_id: Cluster ID
        request: Farmer information
        
    Returns:
        Updated cluster information
    """
    try:
        cluster = coordinator.add_farmer_to_cluster(
            cluster_id=cluster_id,
            farmer_id=request.farmer_id,
            location_name=request.location_name,
            location=(request.latitude, request.longitude),
            quantity_kg=request.quantity_kg,
            cost_individual=request.cost_individual_kes
        )
        
        return {
            "cluster_id": cluster["cluster_id"],
            "members_count": len(cluster["members"]),
            "total_quantity_kg": cluster["total_quantity_kg"],
            "cost_per_farmer_kes": cluster["cost_per_farmer"],
            "savings_percent": cluster["savings_percent"],
            "status": cluster["status"].value,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding farmer: {str(e)}")


@router.post("/{cluster_id}/remove-farmer")
async def remove_farmer_from_cluster(cluster_id: str, request: RemoveFarmerRequest) -> dict:
    """
    Remove a farmer from a cluster.
    
    Args:
        cluster_id: Cluster ID
        request: Farmer ID and reason
        
    Returns:
        Updated cluster information
    """
    try:
        cluster = coordinator.remove_farmer_from_cluster(
            cluster_id=cluster_id,
            farmer_id=request.farmer_id,
            reason=request.reason
        )
        
        return {
            "cluster_id": cluster["cluster_id"],
            "members_count": len(cluster["members"]),
            "total_quantity_kg": cluster["total_quantity_kg"],
            "cost_per_farmer_kes": cluster["cost_per_farmer"],
            "savings_percent": cluster["savings_percent"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing farmer: {str(e)}")


@router.post("/{cluster_id}/commit-farmer")
async def commit_farmer(cluster_id: str, request: CommitFarmerRequest) -> dict:
    """
    Commit a farmer to cluster participation.
    
    Args:
        cluster_id: Cluster ID
        request: Farmer ID
        
    Returns:
        Commitment confirmation
    """
    try:
        member = coordinator.commit_farmer(cluster_id, request.farmer_id)
        
        return {
            "farmer_id": member["farmer_id"],
            "status": member["status"].value,
            "committed_at": member.get("committed_at"),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error committing farmer: {str(e)}")


@router.post("/{cluster_id}/lock")
async def lock_cluster(cluster_id: str) -> dict:
    """
    Lock cluster - no more members can join.
    Cluster is ready for route optimization and shipment.
    
    Args:
        cluster_id: Cluster to lock
        
    Returns:
        Updated cluster with locked status
    """
    try:
        cluster = coordinator.lock_cluster(cluster_id)
        
        return {
            "cluster_id": cluster["cluster_id"],
            "status": cluster["status"].value,
            "members_count": len(cluster["members"]),
            "total_quantity_kg": cluster["total_quantity_kg"],
            "locked_at": cluster.get("locked_at"),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error locking cluster: {str(e)}")


@router.get("/{cluster_id}", response_model=ClusterDetailsResponse)
async def get_cluster_details(cluster_id: str) -> dict:
    """
    Get detailed cluster information.
    
    Args:
        cluster_id: Cluster ID
        
    Returns:
        ClusterDetailsResponse with full cluster details
    """
    try:
        cluster = coordinator.get_cluster(cluster_id)
        
        return ClusterDetailsResponse(
            cluster_id=cluster["cluster_id"],
            cluster_name=cluster["cluster_name"],
            region=cluster["region"],
            produce=cluster["produce"],
            target_market=cluster["target_market"],
            status=cluster["status"].value,
            quality_score=cluster["quality_score"],
            members_count=len(cluster["members"]),
            total_quantity_kg=cluster["total_quantity_kg"],
            total_quantity_sacks=round(cluster["total_quantity_kg"] / 90, 1),
            cost_per_farmer_kes=cluster["cost_per_farmer"],
            savings_percent=cluster["savings_percent"],
            members=[
                {
                    "farmer_id": m["farmer_id"],
                    "location_name": m["location_name"],
                    "quantity_kg": m["quantity_kg"],
                    "cost_individual_kes": m["cost_individual"],
                    "status": m["status"].value,
                }
                for m in cluster["members"]
            ],
            pickup_date=cluster["pickup_date"],
            vehicle_assigned=cluster["vehicle_assigned"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cluster: {str(e)}")


@router.get("", response_model=ClusterListResponse)
async def list_active_clusters(region: str = None, produce: str = None) -> dict:
    """
    List all active (forming) clusters.
    
    Args:
        region: Filter by region (optional)
        produce: Filter by produce type (optional)
        
    Returns:
        List of active clusters
    """
    try:
        clusters = coordinator.get_active_clusters(region=region, produce=produce)
        
        return ClusterListResponse(
            total_clusters=len(clusters),
            clusters=[
                ClusterDetailsResponse(
                    cluster_id=c["cluster_id"],
                    cluster_name=c["cluster_name"],
                    region=c["region"],
                    produce=c["produce"],
                    target_market=c["target_market"],
                    status=c["status"].value,
                    quality_score=c["quality_score"],
                    members_count=len(c["members"]),
                    total_quantity_kg=c["total_quantity_kg"],
                    total_quantity_sacks=round(c["total_quantity_kg"] / 90, 1),
                    cost_per_farmer_kes=c["cost_per_farmer"],
                    savings_percent=c["savings_percent"],
                    members=[],
                    pickup_date=c["pickup_date"],
                    vehicle_assigned=c["vehicle_assigned"],
                )
                for c in clusters
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing clusters: {str(e)}")


# ============================================================================
# ROUTE OPTIMIZATION ENDPOINTS
# ============================================================================

@router.post("/{cluster_id}/optimize-route", response_model=RouteResponse)
async def optimize_route(cluster_id: str, request: GenerateRouteRequest) -> dict:
    """
    Generate optimized pickup route for cluster.
    
    Uses nearest-neighbor algorithm to minimize distance and time.
    
    Args:
        cluster_id: Cluster ID
        request: Market location details
        
    Returns:
        Optimized route with waypoints and cost estimate
    """
    try:
        cluster = coordinator.get_cluster(cluster_id)
        
        if cluster["status"].value != "locked":
            raise ValueError("Cluster must be locked before route optimization")
        
        # Create market location
        market = Location(
            name=request.start_market_name,
            latitude=request.start_market_latitude,
            longitude=request.start_market_longitude
        )
        
        # Create pickup locations from cluster members
        pickup_locations = [
            Location(
                name=m["location_name"],
                latitude=m["location"][0],
                longitude=m["location"][1]
            )
            for m in cluster["members"]
        ]
        
        # Generate route
        route = nearest_neighbor_route(market, pickup_locations)
        
        # Optionally improve with 2-opt
        route = two_opt_improvement(route, pickup_locations, max_iterations=50)
        
        # Generate summary
        summary = generate_route_summary(route, len(cluster["members"]))
        
        return RouteResponse(**summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing route: {str(e)}")


# ============================================================================
# MARKET NEGOTIATION ENDPOINTS
# ============================================================================

@router.get("/{cluster_id}/bulk-pricing")
async def get_bulk_pricing(cluster_id: str) -> BulkPricingResponse:
    """
    Get bulk pricing information for cluster.
    
    Shows how volume improves market price.
    
    Args:
        cluster_id: Cluster ID
        
    Returns:
        Bulk pricing breakdown
    """
    try:
        cluster = coordinator.get_cluster(cluster_id)
        
        # Use base market price (example - would come from prediction service)
        base_price = 25.0  # KES per kg (example)
        
        pricing = calculate_bulk_pricing(
            base_price,
            cluster["total_quantity_kg"],
            cluster["produce"]
        )
        
        return BulkPricingResponse(**pricing)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating pricing: {str(e)}")


@router.get("/{cluster_id}/negotiation-leverage")
async def get_negotiation_leverage(cluster_id: str) -> NegotiationLeverageResponse:
    """
    Get negotiation leverage points for cluster.
    
    Provides talking points for market negotiations.
    
    Args:
        cluster_id: Cluster ID
        
    Returns:
        Negotiation leverage information
    """
    try:
        cluster = coordinator.get_cluster(cluster_id)
        
        leverage = calculate_negotiation_leverage(
            cluster["total_quantity_kg"],
            len(cluster["members"]),
            cluster["produce"]
        )
        
        return NegotiationLeverageResponse(**leverage)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating leverage: {str(e)}")


@router.post("/{cluster_id}/profit-comparison")
async def get_profit_comparison(
    cluster_id: str,
    individual_price_per_kg: float,
    transport_cost_individual: float
) -> ProfitComparisonResponse:
    """
    Compare profit: individual vs clustered.
    
    Shows profit improvement with clustering.
    
    Args:
        cluster_id: Cluster ID
        individual_price_per_kg: Current individual market price
        transport_cost_individual: Individual transport cost (per farmer)
        
    Returns:
        Profit comparison
    """
    try:
        cluster = coordinator.get_cluster(cluster_id)
        
        # Calculate individual revenues
        individual_revenues = [
            m["quantity_kg"] * individual_price_per_kg
            for m in cluster["members"]
        ]
        individual_costs = [transport_cost_individual for _ in cluster["members"]]
        
        # Bulk pricing
        bulk_pricing = calculate_bulk_pricing(
            individual_price_per_kg,
            cluster["total_quantity_kg"],
            cluster["produce"]
        )
        bulk_price_revenue = bulk_pricing["total_additional_revenue"] + sum(individual_revenues)
        
        # Comparison
        comparison = calculate_profit_improvement(
            individual_revenues,
            individual_costs,
            cluster["cost_per_farmer"] * len(cluster["members"]),
            bulk_price_revenue
        )
        
        return ProfitComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing profits: {str(e)}")


# ============================================================================
# SHIPMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{cluster_id}/generate-shipment", response_model=ShipmentResponse)
async def generate_shipment(cluster_id: str, request: GenerateShipmentRequest) -> dict:
    """
    Generate shipment from locked cluster.
    
    Args:
        cluster_id: Cluster ID
        request: Vehicle type and route info
        
    Returns:
        Shipment information
    """
    try:
        shipment = coordinator.generate_shipment(
            cluster_id,
            request.vehicle_type,
            request.route_id,
            request.estimated_cost_kes
        )
        
        return ShipmentResponse(**shipment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shipment: {str(e)}")


@router.get("/{cluster_id}/opportunities")
async def get_clustering_opportunities(
    produce: str = None,
    target_market: str = None,
    region: str = None
) -> dict:
    """
    Get clustering opportunities for farmers.
    
    Identifies potential clusters and savings.
    
    Args:
        produce: Filter by produce type
        target_market: Filter by target market
        region: Filter by region
        
    Returns:
        Available clustering opportunities
    """
    try:
        clusters = coordinator.get_active_clusters(region=region, produce=produce)
        
        opportunities = [
            {
                "opportunity_id": f"opp_{cluster['cluster_id']}",
                "cluster_id": cluster["cluster_id"],
                "region": cluster["region"],
                "produce": cluster["produce"],
                "target_market": cluster["target_market"],
                "potential_members": cluster["members_count"],
                "current_quantity_kg": cluster["total_quantity_kg"],
                "potential_savings_percent": cluster["savings_percent"],
                "cost_per_farmer_kes": cluster["cost_per_farmer"],
                "status": cluster["status"].value,
            }
            for cluster in clusters
        ]
        
        return {
            "total_opportunities": len(opportunities),
            "opportunities": opportunities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding opportunities: {str(e)}")
