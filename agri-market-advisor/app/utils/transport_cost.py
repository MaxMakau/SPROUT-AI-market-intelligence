"""
Transport cost calculation module.
Uses OpenRouteService API for real distance/routing data.
Logs all API interactions for debugging and monitoring.
"""

from typing import Optional
import os
import requests
import logging
from app.utils.constants import TRANSPORT_MODES

# Set up logging for transport cost calculations
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Simple in-memory cache for geocoding results to avoid repeated API calls
_GEOCODE_CACHE = {}


def calculate_transport_cost(
    from_location: str,
    to_market: str,
    transport_mode: str,
    quantity_kg: float
) -> dict:
    """
    Calculate transport cost from location to market using OpenRouteService API.
    
    Requires OPENROUTESERVICE_API_KEY environment variable to be set.
    Raises ValueError if API key is missing or API calls fail.
    
    Args:
        from_location: Starting location (county/city name)
        to_market: Destination market name
        transport_mode: Transport mode (motorbike, pickup, lorry)
        quantity_kg: Quantity in kg
        
    Returns:
        Dictionary with cost breakdown
        
    Raises:
        ValueError: If ORS API key is missing or API fails
    """
    logger.info(f"📍 Transport cost request: {from_location} → {to_market} ({quantity_kg} kg, mode: {transport_mode})")
    
    # Get ORS API key from environment
    ors_key = os.environ.get('OPENROUTESERVICE_API_KEY') or os.environ.get('ORS_API_KEY') or os.environ.get('OPEN_ROUTE_SERVICE_API_KEY')
    
    if not ors_key:
        logger.error("❌ ORS API key not found in environment variables (OPENROUTESERVICE_API_KEY, ORS_API_KEY, OPEN_ROUTE_SERVICE_API_KEY)")
        raise ValueError("OpenRouteService API key not configured. Set OPENROUTESERVICE_API_KEY environment variable.")

    def _geocode_location(text: str):
        """
        Geocode a location name to (lat, lon) using ORS API.
        Results are cached to avoid repeated calls.
        
        Args:
            text: Location name or market name
            
        Returns:
            Tuple of (lat, lon) or None if geocoding fails
        """
        if not text:
            logger.warning("⚠️  Empty location text provided to geocoding")
            return None
        
        key = text.lower().strip()
        if key in _GEOCODE_CACHE:
            logger.debug(f"📦 Geocoding cache HIT for '{text}' → {_GEOCODE_CACHE[key]}")
            return _GEOCODE_CACHE[key]

        logger.debug(f"🔍 Geocoding location '{text}' via ORS API...")
        try:
            url = 'https://api.openrouteservice.org/geocode/search'
            params = {'api_key': ors_key, 'text': text, 'size': 1}
            logger.debug(f"   GET {url} with text='{text}'")
            
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            features = data.get('features') or []
            
            if not features:
                logger.warning(f"⚠️  ORS geocoding returned no results for '{text}'")
                return None
            
            coords = features[0]['geometry']['coordinates']  # [lon, lat]
            lat, lon = coords[1], coords[0]
            result = (lat, lon)
            
            logger.info(f"✅ Geocoded '{text}' → ({lat:.4f}, {lon:.4f})")
            _GEOCODE_CACHE[key] = result
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ORS geocoding API error for '{text}': {e}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"❌ Failed to parse ORS geocoding response for '{text}': {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during geocoding of '{text}': {e}")
            return None

    def _ors_matrix_distance(coord1, coord2, from_text: str, to_text: str):
        """
        Query ORS matrix API for distance between two coordinates.
        
        Args:
            coord1: (lat, lon) for origin
            coord2: (lat, lon) for destination
            from_text: Origin location name (for logging)
            to_text: Destination location name (for logging)
            
        Returns:
            Distance in km, or None if request fails
        """
        if not coord1 or not coord2:
            logger.warning(f"❌ Invalid coordinates provided: {coord1} → {coord2}")
            return None
        
        logger.debug(f"📡 Requesting distance matrix from ORS: ({coord1[0]:.4f}, {coord1[1]:.4f}) → ({coord2[0]:.4f}, {coord2[1]:.4f})")
        
        try:
            url = 'https://api.openrouteservice.org/v2/matrix/driving-car'
            headers = {'Authorization': ors_key, 'Content-Type': 'application/json'}
            # ORS expects locations as [lon, lat]
            locations = [[coord1[1], coord1[0]], [coord2[1], coord2[0]]]
            body = {'locations': locations, 'metrics': ['distance'], 'units': 'm'}
            
            logger.debug(f"   POST {url}")
            logger.debug(f"   Payload: {body}")
            
            resp = requests.post(url, json=body, headers=headers, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            distances = data.get('distances')
            
            if not distances or len(distances) == 0 or len(distances[0]) < 2:
                logger.error(f"❌ ORS matrix response missing distance data: {data}")
                return None
            
            # distances returned in meters by default
            meters = distances[0][1]
            km = float(meters) / 1000.0
            
            logger.info(f"✅ ORS matrix distance: {from_text} → {to_text} = {km:.2f} km")
            return km
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ORS matrix API error ({from_text} → {to_text}): {e}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"❌ Failed to parse ORS matrix response ({from_text} → {to_text}): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error in ORS matrix call ({from_text} → {to_text}): {e}")
            return None

    # Geocode source location
    logger.debug(f"Step 1: Geocoding source location '{from_location}'")
    from_coord = _geocode_location(from_location)
    if not from_coord:
        logger.error(f"❌ Failed to geocode source location '{from_location}'")
        raise ValueError(f"Could not geocode source location: {from_location}")

    # Geocode destination market
    logger.debug(f"Step 2: Geocoding destination market '{to_market}'")
    to_coord = _geocode_location(to_market)
    if not to_coord:
        logger.error(f"❌ Failed to geocode destination market '{to_market}'")
        raise ValueError(f"Could not geocode destination market: {to_market}")

    # Get distance from ORS matrix API
    logger.debug(f"Step 3: Requesting distance via ORS matrix API")
    distance = _ors_matrix_distance(from_coord, to_coord, from_location, to_market)
    if distance is None:
        logger.error(f"❌ Failed to get distance from ORS matrix API")
        raise ValueError(f"Could not calculate distance from ORS: {from_location} → {to_market}")
    
    # Calculate costs
    logger.debug(f"Step 4: Calculating costs based on distance={distance:.2f} km, mode={transport_mode}")
    cost_per_km = TRANSPORT_MODES.get(transport_mode, 5.0)
    
    # Calculate base cost
    base_cost = distance * cost_per_km
    
    # Add minimal handling cost (2% of base cost, minimum 50 KES)
    handling_cost = max(base_cost * 0.02, 50.0)
    
    # Total cost
    total_cost = base_cost + handling_cost
    
    result = {
        "distance_km": distance,
        "cost_per_km": cost_per_km,
        "base_cost": round(base_cost, 2),
        "handling_cost": round(handling_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_kg": round(total_cost / quantity_kg, 2) if quantity_kg > 0 else 0,
        "source": "OpenRouteService API"
    }
    
    logger.info(f"✅ Transport cost calculated: {total_cost:.2f} KES ({result['cost_per_kg']:.2f} KES/kg)")
    return result


def get_optimal_transport_mode(
    distance: float,
    quantity_kg: float
) -> str:
    """
    Recommend optimal transport mode based on distance and quantity.
    
    Args:
        distance: Distance in km
        quantity_kg: Quantity in kg
        
    Returns:
        Recommended transport mode
    """
    if quantity_kg < 50 and distance < 100:
        return "motorbike"
    elif quantity_kg < 500 and distance < 200:
        return "pickup"
    else:
        return "lorry"


def estimate_transport_time(
    distance: float,
    transport_mode: str
) -> dict:
    """
    Estimate transport time and conditions.
    
    Args:
        distance: Distance in km
        transport_mode: Transport mode
        
    Returns:
        Dictionary with time estimates
    """
    # Average speeds (km/h)
    speeds = {
        "motorbike": 40,
        "pickup": 50,
        "lorry": 40
    }
    
    speed = speeds.get(transport_mode, 50)
    travel_time_hours = distance / speed
    
    return {
        "distance_km": distance,
        "transport_mode": transport_mode,
        "speed_kmh": speed,
        "travel_time_hours": travel_time_hours,
        "travel_time_minutes": travel_time_hours * 60,
        "estimated_arrival": f"~{int(travel_time_hours)} hour(s)"
    }


def compare_transport_costs(
    from_location: str,
    to_market: str,
    quantity_kg: float
) -> dict:
    """
    Compare costs across all transport modes.
    
    Args:
        from_location: Starting location
        to_market: Destination market
        quantity_kg: Quantity in kg
        
    Returns:
        Dictionary with comparison
    """
    comparison = {}
    
    for mode in TRANSPORT_MODES.keys():
        cost_info = calculate_transport_cost(
            from_location,
            to_market,
            mode,
            quantity_kg
        )
        comparison[mode] = cost_info
    
    # Find cheapest
    cheapest_mode = min(
        comparison.keys(),
        key=lambda m: comparison[m]["total_cost"]
    )
    
    return {
        "all_modes": comparison,
        "cheapest_mode": cheapest_mode,
        "cheapest_cost": comparison[cheapest_mode]["total_cost"],
        "recommendations": {
            mode: {
                "cost": comparison[mode]["total_cost"],
                "cost_per_kg": comparison[mode]["cost_per_kg"],
                "rank": list(sorted(comparison.keys(), 
                           key=lambda m: comparison[m]["total_cost"])).index(mode) + 1
            }
            for mode in comparison
        }
    }
