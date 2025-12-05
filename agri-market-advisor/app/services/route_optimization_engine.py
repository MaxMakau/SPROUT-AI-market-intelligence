"""
Route optimization engine for planning efficient collection routes.
Minimizes distance and time while collecting produce from multiple farmers.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class Location:
    """Represents a geographic location."""
    name: str
    latitude: float
    longitude: float


@dataclass
class Waypoint:
    """Represents a stop on a route."""
    location: Location
    order: int
    cumulative_distance_km: float
    estimated_arrival_minutes: int


@dataclass
class Route:
    """Optimized route for collection."""
    route_id: str
    waypoints: List[Waypoint]
    total_distance_km: float
    estimated_duration_minutes: int
    vehicle_type: str


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
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


def nearest_neighbor_route(
    start_location: Location,
    pickup_locations: List[Location],
    avg_speed_kmh: float = 40.0
) -> Route:
    """
    Find near-optimal route using nearest neighbor algorithm.
    
    Algorithm:
    1. Start at market location
    2. Go to nearest unvisited pickup point
    3. From there, go to next nearest unvisited point
    4. Repeat until all pickups done, then return to market
    
    Time Complexity: O(n²)
    Optimality: ~85-90% of optimal (good for practical use)
    
    Args:
        start_location: Starting point (market)
        pickup_locations: List of farmer locations to visit
        avg_speed_kmh: Average travel speed in km/h
        
    Returns:
        Optimized route
    """
    if not pickup_locations:
        return Route(
            route_id="empty_route",
            waypoints=[],
            total_distance_km=0,
            estimated_duration_minutes=0,
            vehicle_type="none"
        )
    
    visited = set()
    waypoints = []
    current_location = start_location
    total_distance = 0
    order = 0
    
    # Create waypoint for starting location
    waypoints.append(Waypoint(
        location=start_location,
        order=order,
        cumulative_distance_km=0,
        estimated_arrival_minutes=0
    ))
    order += 1
    
    # Visit each location using nearest neighbor
    while len(visited) < len(pickup_locations):
        nearest_idx = -1
        nearest_distance = float('inf')
        
        # Find nearest unvisited location
        for i, location in enumerate(pickup_locations):
            if i in visited:
                continue
            
            dist = haversine_distance(
                current_location.latitude, current_location.longitude,
                location.latitude, location.longitude
            )
            
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_idx = i
        
        if nearest_idx == -1:
            break
        
        # Add to route
        visited.add(nearest_idx)
        total_distance += nearest_distance
        arrival_minutes = int((total_distance / avg_speed_kmh) * 60)
        
        waypoints.append(Waypoint(
            location=pickup_locations[nearest_idx],
            order=order,
            cumulative_distance_km=round(total_distance, 2),
            estimated_arrival_minutes=arrival_minutes
        ))
        order += 1
        
        current_location = pickup_locations[nearest_idx]
    
    # Return to start location (market)
    return_distance = haversine_distance(
        current_location.latitude, current_location.longitude,
        start_location.latitude, start_location.longitude
    )
    total_distance += return_distance
    final_arrival_minutes = int((total_distance / avg_speed_kmh) * 60)
    
    waypoints.append(Waypoint(
        location=start_location,
        order=order,
        cumulative_distance_km=round(total_distance, 2),
        estimated_arrival_minutes=final_arrival_minutes
    ))
    
    # Determine vehicle type based on distance
    if total_distance <= 50:
        vehicle_type = "pickup"
    elif total_distance <= 150:
        vehicle_type = "pickup"
    else:
        vehicle_type = "lorry"
    
    estimated_duration_minutes = int((total_distance / avg_speed_kmh) * 60) + (len(pickup_locations) * 10)  # 10 min per stop
    
    return Route(
        route_id=f"route_{start_location.name}",
        waypoints=waypoints,
        total_distance_km=round(total_distance, 2),
        estimated_duration_minutes=estimated_duration_minutes,
        vehicle_type=vehicle_type
    )


def two_opt_improvement(
    route: Route,
    pickup_locations: List[Location],
    max_iterations: int = 100
) -> Route:
    """
    Improve route using 2-opt local search algorithm.
    Swaps edges to reduce total distance.
    
    Algorithm:
    1. Take route with edges (a,b) and (c,d)
    2. Replace with (a,c) and (b,d)
    3. Keep if distance decreases
    4. Repeat until no improvement
    
    Time Complexity: O(n²) per iteration
    Improvement: Typically 5-15% improvement over nearest neighbor
    
    Args:
        route: Initial route
        pickup_locations: List of locations
        max_iterations: Maximum iterations to try
        
    Returns:
        Improved route
    """
    if not pickup_locations or len(pickup_locations) < 4:
        return route
    
    # Create list of indices (skip first and last which are market)
    waypoint_indices = list(range(1, len(route.waypoints) - 1))
    best_distance = route.total_distance_km
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(len(waypoint_indices) - 1):
            for j in range(i + 2, len(waypoint_indices)):
                # Reverse the segment between i+1 and j (inclusive)
                new_indices = waypoint_indices[:i+1] + waypoint_indices[i+1:j+1][::-1] + waypoint_indices[j+1:]
                
                # Calculate new distance after swap
                new_distance = _calculate_route_distance(route.waypoints, new_indices)
                
                # Keep improvement if distance reduced
                if new_distance < best_distance:
                    waypoint_indices = new_indices
                    best_distance = new_distance
                    improved = True
                    break
            
            if improved:
                break
    
    # Rebuild route with optimized order
    optimized_waypoints = [route.waypoints[0]]  # Start
    cumulative_distance = 0
    
    for idx in waypoint_indices:
        prev = optimized_waypoints[-1]
        curr = route.waypoints[idx]
        
        dist = haversine_distance(
            prev.location.latitude, prev.location.longitude,
            curr.location.latitude, curr.location.longitude
        )
        cumulative_distance += dist
        
        optimized_waypoints.append(Waypoint(
            location=curr.location,
            order=len(optimized_waypoints),
            cumulative_distance_km=round(cumulative_distance, 2),
            estimated_arrival_minutes=int((cumulative_distance / 40) * 60)
        ))
    
    # Add return to start
    final_dist = haversine_distance(
        optimized_waypoints[-1].location.latitude,
        optimized_waypoints[-1].location.longitude,
        route.waypoints[0].location.latitude,
        route.waypoints[0].location.longitude
    )
    cumulative_distance += final_dist
    
    optimized_waypoints.append(Waypoint(
        location=route.waypoints[0].location,
        order=len(optimized_waypoints),
        cumulative_distance_km=round(cumulative_distance, 2),
        estimated_arrival_minutes=int((cumulative_distance / 40) * 60)
    ))
    
    return Route(
        route_id=route.route_id,
        waypoints=optimized_waypoints,
        total_distance_km=round(cumulative_distance, 2),
        estimated_duration_minutes=int((cumulative_distance / 40) * 60) + (len(waypoint_indices) * 10),
        vehicle_type=route.vehicle_type
    )


def _calculate_route_distance(waypoints: List[Waypoint], indices: List[int]) -> float:
    """
    Calculate total distance for a specific sequence of waypoints.
    
    Args:
        waypoints: List of all waypoints
        indices: Indices in order to traverse
        
    Returns:
        Total distance
    """
    total = 0
    for i in range(len(indices) - 1):
        curr = waypoints[indices[i]]
        next_wp = waypoints[indices[i + 1]]
        
        dist = haversine_distance(
            curr.location.latitude, curr.location.longitude,
            next_wp.location.latitude, next_wp.location.longitude
        )
        total += dist
    
    return total


def estimate_pickup_time(
    route: Route,
    minutes_per_stop: int = 10
) -> Dict[str, int]:
    """
    Estimate time for entire route including collection.
    
    Args:
        route: Optimized route
        minutes_per_stop: Time spent at each pickup point
        
    Returns:
        Dictionary with time breakdown
    """
    travel_time = int((route.total_distance_km / 40.0) * 60)  # 40 km/h average
    collection_time = (len(route.waypoints) - 2) * minutes_per_stop  # Exclude start and end
    total_time = travel_time + collection_time
    
    return {
        "travel_time_minutes": travel_time,
        "collection_time_minutes": collection_time,
        "total_time_minutes": total_time,
        "total_time_hours": round(total_time / 60, 1),
    }


def estimate_route_cost(
    route: Route,
    vehicle_costs: Dict[str, float] = None
) -> Dict[str, float]:
    """
    Estimate route cost based on distance and vehicle type.
    
    Args:
        route: Optimized route
        vehicle_costs: Cost per km by vehicle type (default provided)
        
    Returns:
        Cost breakdown
    """
    if vehicle_costs is None:
        vehicle_costs = {
            "motorbike": 30.0,  # KES per km
            "pickup": 25.0,
            "lorry": 20.0,
        }
    
    cost_per_km = vehicle_costs.get(route.vehicle_type, 25.0)
    total_cost = route.total_distance_km * cost_per_km
    
    return {
        "vehicle_type": route.vehicle_type,
        "distance_km": route.total_distance_km,
        "cost_per_km": cost_per_km,
        "total_cost_kes": round(total_cost, 2),
    }


def generate_route_summary(
    route: Route,
    farmer_count: int
) -> Dict:
    """
    Generate comprehensive summary of optimized route.
    
    Args:
        route: Optimized route
        farmer_count: Number of farmers in cluster
        
    Returns:
        Summary dictionary
    """
    time_estimate = estimate_pickup_time(route)
    cost_estimate = estimate_route_cost(route)
    
    cost_per_farmer = cost_estimate["total_cost_kes"] / farmer_count if farmer_count > 0 else 0
    
    return {
        "route_id": route.route_id,
        "total_distance_km": route.total_distance_km,
        "total_stops": len(route.waypoints) - 2,  # Exclude start and end
        "vehicle_type": route.vehicle_type,
        "time": time_estimate,
        "cost": cost_estimate,
        "cost_per_farmer_kes": round(cost_per_farmer, 2),
        "waypoints": [
            {
                "order": wp.order,
                "location": wp.location.name,
                "cumulative_distance_km": wp.cumulative_distance_km,
                "estimated_arrival_minutes": wp.estimated_arrival_minutes,
            }
            for wp in route.waypoints
        ],
    }
