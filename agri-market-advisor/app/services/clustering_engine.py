"""
Clustering engine for grouping farmers by geography and product type.
Enables consolidation of shipments for cost optimization.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class Farmer:
    """Represents a farmer for clustering purposes."""
    farmer_id: str
    location: Tuple[float, float]  # (latitude, longitude)
    produce: str
    quantity_kg: float
    location_name: str


@dataclass
class Cluster:
    """Represents a group of farmers for consolidated shipment."""
    cluster_id: str
    region: str
    produce: str
    target_market: str
    members: List[Farmer]
    total_quantity_kg: float
    quality_score: float


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two geographic points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_proximity_score(distances: List[float], max_radius_km: float = 15.0) -> float:
    """
    Calculate proximity quality score (0-1).
    Farmers closer together = higher score.
    
    Args:
        distances: List of distances between cluster members
        max_radius_km: Maximum acceptable radius
        
    Returns:
        Proximity score (0-1, where 1 is ideal)
    """
    if not distances:
        return 1.0
    
    avg_distance = sum(distances) / len(distances)
    
    # Penalize if average distance exceeds max radius
    if avg_distance > max_radius_km:
        return max(0, 1 - (avg_distance - max_radius_km) / max_radius_km)
    
    # Score decreases as distance increases
    return 1 - (avg_distance / max_radius_km)


def calculate_product_match_score(produces: List[str]) -> float:
    """
    Calculate product match quality score (0-1).
    All same product = 1.0, mixed = lower scores.
    
    Args:
        produces: List of produce types in cluster
        
    Returns:
        Product match score (0-1)
    """
    if not produces:
        return 0
    
    # Count occurrences of most common product
    most_common_count = max(produces.count(p) for p in set(produces))
    
    # Score based on how many match the most common
    return most_common_count / len(produces)


def calculate_vehicle_efficiency_score(total_quantity_kg: float, sack_size_kg: int = 90) -> float:
    """
    Calculate vehicle efficiency score (0-1).
    Based on how full the vehicle will be.
    
    Args:
        total_quantity_kg: Total quantity in kg
        sack_size_kg: Weight per sack (default 90kg)
        
    Returns:
        Efficiency score (0-1)
    """
    total_sacks = total_quantity_kg / sack_size_kg
    
    # Pickup capacity: ~20 sacks, Lorry capacity: ~40 sacks
    if total_sacks <= 3:
        # Motorbike/small vehicle - good if <= 3
        return min(1.0, total_sacks / 3.0)
    elif total_sacks <= 20:
        # Pickup vehicle - good if 80%+ full (16 sacks)
        return min(1.0, total_sacks / 20.0)
    else:
        # Lorry vehicle - good if 80%+ full (32 sacks)
        return min(1.0, total_sacks / 40.0)


def calculate_quantity_viability_score(total_quantity_kg: float, min_sacks: float = 3.0, sack_size_kg: int = 90) -> float:
    """
    Calculate if shipment size is viable (0-1).
    Too small = wasted trip, too large = multiple vehicles needed.
    
    Args:
        total_quantity_kg: Total quantity in kg
        min_sacks: Minimum viable sacks (default 3)
        sack_size_kg: Weight per sack (default 90kg)
        
    Returns:
        Viability score (0-1)
    """
    total_sacks = total_quantity_kg / sack_size_kg
    
    # Ideal range: 5-30 sacks (one vehicle)
    if total_sacks < min_sacks:
        return total_sacks / min_sacks
    elif total_sacks > 35:
        # Would need multiple vehicles, penalty
        return max(0.5, 35 / total_sacks)
    else:
        return 1.0


def calculate_cluster_quality_score(
    farmers: List[Farmer],
    target_market: str,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate overall cluster quality score (0-1).
    Higher score = better clustering.
    
    Args:
        farmers: List of farmers in potential cluster
        target_market: Target market location
        weights: Custom weights for scoring factors
        
    Returns:
        Overall quality score (0-1)
    """
    if not farmers or len(farmers) < 2:
        return 0
    
    # Default weights
    if weights is None:
        weights = {
            "proximity": 0.25,
            "product": 0.25,
            "quantity": 0.20,
            "vehicle": 0.20,
            "count": 0.10  # Bonus for larger clusters
        }
    
    # Calculate proximity score
    distances = []
    for i, farmer1 in enumerate(farmers):
        for farmer2 in farmers[i+1:]:
            dist = haversine_distance(
                farmer1.location[0], farmer1.location[1],
                farmer2.location[0], farmer2.location[1]
            )
            distances.append(dist)
    
    proximity = calculate_proximity_score(distances)
    
    # Calculate product match score
    products = [f.produce.lower() for f in farmers]
    product_match = calculate_product_match_score(products)
    
    # Calculate quantity viability
    total_quantity = sum(f.quantity_kg for f in farmers)
    quantity_score = calculate_quantity_viability_score(total_quantity)
    
    # Calculate vehicle efficiency
    vehicle_score = calculate_vehicle_efficiency_score(total_quantity)
    
    # Bonus for cluster size (more farmers = more valuable consolidation)
    # Ideal size: 5-8 farmers
    count_score = min(1.0, len(farmers) / 8.0)
    
    # Weighted sum
    overall_score = (
        proximity * weights["proximity"] +
        product_match * weights["product"] +
        quantity_score * weights["quantity"] +
        vehicle_score * weights["vehicle"] +
        count_score * weights["count"]
    )
    
    return overall_score


def find_clusters(
    farmers: List[Farmer],
    target_market: str,
    max_radius_km: float = 15.0,
    min_cluster_size: int = 3,
    min_quality_score: float = 0.5
) -> List[Cluster]:
    """
    Find optimal clusters of farmers for consolidation.
    
    Algorithm: Group farmers by produce type, then by proximity.
    
    Args:
        farmers: List of farmers to cluster
        target_market: Target market for shipment
        max_radius_km: Maximum distance between cluster members
        min_cluster_size: Minimum farmers per cluster
        min_quality_score: Minimum quality score to form cluster
        
    Returns:
        List of viable clusters
    """
    if not farmers:
        return []
    
    # Step 1: Group by produce type
    by_produce = {}
    for farmer in farmers:
        produce = farmer.produce.lower()
        if produce not in by_produce:
            by_produce[produce] = []
        by_produce[produce].append(farmer)
    
    clusters = []
    cluster_counter = 0
    
    # Step 2: For each produce type, find geographic clusters
    for produce, farmers_of_type in by_produce.items():
        if len(farmers_of_type) < min_cluster_size:
            continue
        
        # Sort by location (use latitude as primary sort)
        sorted_farmers = sorted(farmers_of_type, key=lambda f: (f.location[0], f.location[1]))
        
        # Find clusters within this produce group
        used = set()
        
        for i, farmer in enumerate(sorted_farmers):
            if i in used:
                continue
            
            # Start new cluster with this farmer
            cluster_members = [farmer]
            used.add(i)
            
            # Find nearby farmers
            for j, other_farmer in enumerate(sorted_farmers):
                if j <= i or j in used:
                    continue
                
                dist = haversine_distance(
                    farmer.location[0], farmer.location[1],
                    other_farmer.location[0], other_farmer.location[1]
                )
                
                # Add to cluster if within radius
                if dist <= max_radius_km:
                    cluster_members.append(other_farmer)
                    used.add(j)
            
            # Check if cluster is viable
            if len(cluster_members) >= min_cluster_size:
                quality = calculate_cluster_quality_score(cluster_members, target_market)
                
                if quality >= min_quality_score:
                    total_quantity = sum(f.quantity_kg for f in cluster_members)
                    
                    cluster = Cluster(
                        cluster_id=f"cluster_{cluster_counter}",
                        region=_infer_region(cluster_members),
                        produce=produce,
                        target_market=target_market,
                        members=cluster_members,
                        total_quantity_kg=total_quantity,
                        quality_score=quality
                    )
                    
                    clusters.append(cluster)
                    cluster_counter += 1
    
    # Sort by quality score (best first)
    return sorted(clusters, key=lambda c: c.quality_score, reverse=True)


def _infer_region(farmers: List[Farmer]) -> str:
    """
    Infer region from farmer locations.
    
    Args:
        farmers: List of farmers
        
    Returns:
        Region name (or generic location description)
    """
    # This is a simple implementation that uses location names
    # In production, you'd use proper geocoding
    if not farmers:
        return "Unknown"
    
    # Count location names and return most common
    locations = [f.location_name for f in farmers]
    most_common = max(set(locations), key=locations.count)
    
    return most_common


def calculate_consolidation_savings(
    individual_costs: List[float],
    consolidated_cost: float
) -> Dict[str, float]:
    """
    Calculate savings from consolidation.
    
    Args:
        individual_costs: Cost for each farmer if shipping alone
        consolidated_cost: Total cost if consolidated
        
    Returns:
        Dictionary with savings metrics
    """
    total_individual = sum(individual_costs)
    cost_per_farmer = consolidated_cost / len(individual_costs)
    
    return {
        "total_individual_cost": total_individual,
        "total_consolidated_cost": consolidated_cost,
        "total_savings": total_individual - consolidated_cost,
        "savings_percent": ((total_individual - consolidated_cost) / total_individual * 100) if total_individual > 0 else 0,
        "savings_per_farmer": total_individual / len(individual_costs) - cost_per_farmer,
        "savings_percent_per_farmer": ((total_individual / len(individual_costs) - cost_per_farmer) / (total_individual / len(individual_costs)) * 100) if total_individual > 0 else 0,
    }
