import math
import requests

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the Haversine distance between two points"""
    # Radius of earth in kilometers
    R = 6371.0
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def get_osrm_route(start_lat, start_lon, end_lat, end_lon):
    """Get routing data from OSRM service"""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data['code'] == 'Ok':
            route = data['routes'][0]
            return {
                'distance': route['distance'] / 1000,  # Convert to km
                'duration': route['duration'] / 60,    # Convert to minutes
                'geometry': route['geometry']
            }
    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"Error getting OSRM route: {e}")
    
    # Fallback to straight line if OSRM fails
    return {
        'distance': haversine_distance(start_lat, start_lon, end_lat, end_lon),
        'duration': haversine_distance(start_lat, start_lon, end_lat, end_lon) * 2,  # Rough estimate
        'geometry': {
            'type': 'LineString',
            'coordinates': [[start_lon, start_lat], [end_lon, end_lat]]
        }
    }

def calculate_weights(hospital, ambulance_loc, emergency_level):
    """Calculate weights for hospital based on distance, priority and capacity"""
    # Calculate distance
    distance = haversine_distance(
        ambulance_loc['lat'], ambulance_loc['lng'],
        hospital['lat'], hospital['lng']
    )
    
    # Base weight is the distance
    weight = distance
    
    # Adjust weight based on emergency level and hospital priority
    if emergency_level == 'high':
        weight = weight / (hospital['priority'] + 0.5)
    elif emergency_level == 'medium':
        weight = weight / (hospital['priority'] * 0.3 + 0.7)
    
    # Adjust for capacity
    if hospital['capacity'] < 30:
        weight *= 1.2
    elif hospital['capacity'] < 50:
        weight *= 1.1
    
    return weight