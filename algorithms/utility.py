# utility.py - Put this in your algorithms folder
import math
import requests

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_route_from_osrm(lat1, lon1, lat2, lon2):
    """Get route information from OSRM service"""
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    url = f"{base_url}{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["code"] == "Ok":
            route = data["routes"][0]
            return {
                "distance": route["distance"] / 1000,  # Convert to km
                "duration": route["duration"] / 60,    # Convert to minutes
                "geometry": route["geometry"]
            }
        else:
            # Fallback if OSRM fails
            return {
                "distance": haversine_distance(lat1, lon1, lat2, lon2),
                "duration": haversine_distance(lat1, lon1, lat2, lon2) * 2,  # Rough estimate
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon1, lat1], [lon2, lat2]]
                }
            }
    except Exception as e:
        # Fallback in case of network issues
        return {
            "distance": haversine_distance(lat1, lon1, lat2, lon2),
            "duration": haversine_distance(lat1, lon1, lat2, lon2) * 2,  # Rough estimate
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon1, lat1], [lon2, lat2]]
            }
        }