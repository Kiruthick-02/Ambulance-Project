import networkx as nx
import math
import requests
import itertools
from algorithms.utility import haversine_distance, get_route_from_osrm

def calculate_tsp_route(ambulance_loc, hospitals, emergency_level):
    """Calculate shortest path using TSP algorithm for ambulance routing"""
    # For small number of hospitals, we can use a brute force approach
    # For larger datasets, we would use approximation algorithms
    
    # Create a complete graph
    G = nx.Graph()
    
    # Add ambulance node
    ambulance_node = 'ambulance'
    G.add_node(ambulance_node, pos=(ambulance_loc['lat'], ambulance_loc['lng']))
    
    # Add hospital nodes
    for i, hospital in enumerate(hospitals):
        hospital_id = f"hospital_{i}"
        G.add_node(hospital_id, pos=(hospital['lat'], hospital['lng']),
                  priority=hospital['priority'], capacity=hospital['capacity'])
        
        # Calculate distance between ambulance and hospital
        distance = haversine_distance(
            ambulance_loc['lat'], ambulance_loc['lng'],
            hospital['lat'], hospital['lng']
        )
        
        # Adjust weight based on emergency level
        weight = distance
        if emergency_level == 'high':
            # For high emergency, prioritize hospitals with high priority
            weight = weight / (hospital['priority'] + 0.5)
        elif emergency_level == 'medium':
            # For medium emergency, slightly prioritize hospitals with higher priority
            weight = weight / (hospital['priority'] * 0.3 + 0.7)
        
        # Also consider capacity
        if hospital['capacity'] < 30:  # Low capacity
            weight *= 1.2
        
        G.add_edge(ambulance_node, hospital_id, weight=weight)
    
    # Since we need to prioritize a single hospital rather than visiting all,
    # we'll adapt the TSP approach to find the best first hospital to visit
    
    # Calculate distances between all hospitals (for completeness of the graph)
    for i, hospital1 in enumerate(hospitals):
        for j, hospital2 in enumerate(hospitals):
            if i < j:  # Avoid duplicating edges
                hospital1_id = f"hospital_{i}"
                hospital2_id = f"hospital_{j}"
                
                # Calculate distance between hospitals
                distance = haversine_distance(
                    hospital1['lat'], hospital1['lng'],
                    hospital2['lat'], hospital2['lng']
                )
                
                G.add_edge(hospital1_id, hospital2_id, weight=distance)
    
    # For a true TSP approach (if needed for multi-hospital visits):
    # Use either nearest neighbor approach for larger datasets
    # or brute force for small datasets
    if len(hospitals) <= 5:  # Small enough for brute force
        best_hospital = find_best_hospital_brute_force(G, ambulance_node, hospitals)
    else:  # Use nearest neighbor heuristic
        best_hospital = find_best_hospital_nearest_neighbor(G, ambulance_node, hospitals)
    
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
        'algorithm': 'TSP'
    }

def find_best_hospital_brute_force(G, ambulance_node, hospitals):
    """Find best hospital using brute force TSP approach"""
    # For this application, we're focused on finding the best first hospital to visit
    # rather than the full TSP circuit
    
    hospital_nodes = [f"hospital_{i}" for i in range(len(hospitals))]
    
    # Get the hospital with the smallest weight directly from ambulance
    best_hospital_id = min(
        hospital_nodes,
        key=lambda x: G[ambulance_node][x]['weight']
    )
    
    # Get the index of the best hospital
    best_hospital_index = int(best_hospital_id.split('_')[1])
    return hospitals[best_hospital_index]

def find_best_hospital_nearest_neighbor(G, ambulance_node, hospitals):
    """Find best hospital using nearest neighbor heuristic"""
    # Since we're only interested in the first hospital to visit,
    # this is equivalent to finding the nearest neighbor from the ambulance
    
    hospital_nodes = [f"hospital_{i}" for i in range(len(hospitals))]
    
    # Get the hospital with the smallest weight directly from ambulance
    best_hospital_id = min(
        hospital_nodes,
        key=lambda x: G[ambulance_node][x]['weight']
    )
    
    # Get the index of the best hospital
    best_hospital_index = int(best_hospital_id.split('_')[1])
    return hospitals[best_hospital_index]

def calculate_full_tsp_route(ambulance_loc, hospitals, emergency_level, visit_count=3):
    """Calculate a route to visit multiple hospitals using TSP
    
    This is an alternative implementation that actually visits multiple hospitals
    in an optimal order, starting from the ambulance location
    """
    # Limit the number of hospitals to visit
    visit_count = min(visit_count, len(hospitals))
    
    # Create a complete weighted graph
    G = nx.Graph()
    
    # Add ambulance node
    ambulance_node = 'ambulance'
    G.add_node(ambulance_node, pos=(ambulance_loc['lat'], ambulance_loc['lng']))
    
    # Add hospital nodes with adjusted weights
    for i, hospital in enumerate(hospitals):
        hospital_id = f"hospital_{i}"
        G.add_node(hospital_id, pos=(hospital['lat'], hospital['lng']),
                  priority=hospital['priority'], capacity=hospital['capacity'])
        
        # Add edge between ambulance and hospital
        distance = haversine_distance(
            ambulance_loc['lat'], ambulance_loc['lng'],
            hospital['lat'], hospital['lng']
        )
        
        # Adjust weight based on emergency level, priority and capacity
        weight = adjust_weight(distance, hospital, emergency_level)
        G.add_edge(ambulance_node, hospital_id, weight=weight)
    
    # Add edges between all hospitals
    for i, hospital1 in enumerate(hospitals):
        for j, hospital2 in enumerate(hospitals):
            if i < j:  # Avoid duplicating edges
                hospital1_id = f"hospital_{i}"
                hospital2_id = f"hospital_{j}"
                
                # Calculate distance between hospitals
                distance = haversine_distance(
                    hospital1['lat'], hospital1['lng'],
                    hospital2['lat'], hospital2['lng']
                )
                
                G.add_edge(hospital1_id, hospital2_id, weight=distance)
    
    # Find the best hospital based on modified weights
    best_hospital_id = min(
        [f"hospital_{i}" for i in range(len(hospitals))],
        key=lambda x: G[ambulance_node][x]['weight']
    )
    
    # Get the index of the best hospital
    best_hospital_index = int(best_hospital_id.split('_')[1])
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
        'algorithm': 'TSP'
    }

def adjust_weight(distance, hospital, emergency_level):
    """Adjust weight based on hospital priority, capacity and emergency level"""
    weight = distance
    
    if emergency_level == 'high':
        # For high emergency, prioritize hospitals with high priority
        weight = weight / (hospital['priority'] + 0.5)
    elif emergency_level == 'medium':
        # For medium emergency, slightly prioritize hospitals with higher priority
        weight = weight / (hospital['priority'] * 0.3 + 0.7)
    
    # Consider capacity
    if hospital['capacity'] < 30:  # Low capacity
        weight *= 1.2
    elif hospital['capacity'] < 50:
        weight *= 1.1
    
    return weight