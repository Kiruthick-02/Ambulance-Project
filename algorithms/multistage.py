import networkx as nx
import math
from algorithms.tsp import haversine_distance, get_route_from_osrm

def calculate_multistage_route(ambulance_loc, hospitals, emergency_level):
    """
    Calculate route using multistage graph algorithm that considers:
    - Hospital distances
    - Emergency capacity
    - Priority level
    """
    # For multistage graph, we'll create a directed graph with stages:
    # Stage 1: Ambulance -> Potential hospitals (weighted by distance)
    # Stage 2: Hospital suitability (weighted by capacity and priority)
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add ambulance node at stage 0
    ambulance_node = 'ambulance'
    G.add_node(ambulance_node, stage=0, pos=(ambulance_loc['lat'], ambulance_loc['lng']))
    
    # Add hospital nodes at stage 1 with connections from ambulance
    for i, hospital in enumerate(hospitals):
        hospital_id = f"hospital_{i}"
        G.add_node(hospital_id, stage=1, 
                  pos=(hospital['lat'], hospital['lng']),
                  priority=hospital['priority'],
                  capacity=hospital['capacity'])
        
        # Calculate distance from ambulance to hospital
        distance = haversine_distance(
            ambulance_loc['lat'], ambulance_loc['lng'],
            hospital['lat'], hospital['lng']
        )
        
        # Base weight is the distance
        weight = distance
        
        # Connect ambulance to hospital with base weight
        G.add_edge(ambulance_node, hospital_id, weight=weight)
    
    # Add a sink node at stage 2
    sink_node = 'sink'
    G.add_node(sink_node, stage=2)
    
    # Connect hospitals to sink with weights based on suitability
    for i, hospital in enumerate(hospitals):
        hospital_id = f"hospital_{i}"
        
        # Calculate suitability weight based on capacity and priority
        capacity_weight = 0
        if hospital['capacity'] < 30:
            capacity_weight = 3  # High penalty for low capacity
        elif hospital['capacity'] < 60:
            capacity_weight = 1  # Medium penalty for medium capacity
        else:
            capacity_weight = 0  # No penalty for high capacity
        
        # Priority weight (inverse of priority - lower is better)
        priority_weight = (5 - hospital['priority']) * 2
        
        # Adjust weights based on emergency level
        if emergency_level == 'high':
            priority_weight *= 2  # Priority is more important for high emergency
        elif emergency_level == 'low':
            capacity_weight *= 0.5  # Capacity is less important for low emergency
        
        # Total suitability weight
        suitability_weight = capacity_weight + priority_weight
        
        # Connect hospital to sink
        G.add_edge(hospital_id, sink_node, weight=suitability_weight)
    
    # Find shortest path from ambulance to sink
    try:
        path = nx.shortest_path(G, ambulance_node, sink_node, weight='weight')
        path_length = nx.shortest_path_length(G, ambulance_node, sink_node, weight='weight')
    except:
        # Fallback if path cannot be found
        return calculate_fallback_multistage(ambulance_loc, hospitals, emergency_level)
    
    # Extract the hospital from the path
    if len(path) >= 2:
        hospital_id = path[1]  # Second node in path (after ambulance)
        hospital_index = int(hospital_id.split('_')[1])
        best_hospital = hospitals[hospital_index]
        
        # Get actual route using OSRM
        route = get_route_from_osrm(
            ambulance_loc['lat'], ambulance_loc['lng'],
            best_hospital['lat'], best_hospital['lng']
        )
        
        return {
            'hospital': best_hospital,
            'distance': route['distance'],
            'duration': route['duration'],
            'route': route['geometry'],
            'algorithm': 'Multistage Graph'
        }
    else:
        return calculate_fallback_multistage(ambulance_loc, hospitals, emergency_level)

def calculate_fallback_multistage(ambulance_loc, hospitals, emergency_level):
    """Fallback method for multistage if path finding fails"""
    # Combine distance with weighted priority and capacity
    hospital_scores = []
    
    for i, hospital in enumerate(hospitals):
        # Calculate direct distance
        distance = haversine_distance(
            ambulance_loc['lat'], ambulance_loc['lng'],
            hospital['lat'], hospital['lng']
        )
        
        # Calculate score based on distance, priority and capacity
        priority_factor = hospital['priority'] / 5.0  # Normalize to 0-1
        capacity_factor = min(1.0, hospital['capacity'] / 100.0)  # Normalize to 0-1
        
        if emergency_level == 'high':
            score = distance * (1.3 - priority_factor * 0.8) * (1.3 - capacity_factor * 0.3)
        elif emergency_level == 'medium':
            score = distance * (1.2 - priority_factor * 0.6) * (1.2 - capacity_factor * 0.2)
        else:  # low
            score = distance * (1.1 - priority_factor * 0.3) * (1.1 - capacity_factor * 0.1)
        
        hospital_scores.append((i, score))
    
    # Select hospital with lowest score
    best_hospital_index, _ = min(hospital_scores, key=lambda x: x[1])
    best_hospital = hospitals[best_hospital_index]
    
    # Get the actual route using OSRM
    route = get_route_from_osrm(
        ambulance_loc['lat'], ambulance_loc['lng'],
        best_hospital['lat'], best_hospital['lng']
    )
    
    return {
        'hospital': best_hospital,
        'distance': route['distance'],
        'duration': route['duration'],
        'route': route['geometry'],
        'algorithm': 'Multistage Graph (fallback)'
    }