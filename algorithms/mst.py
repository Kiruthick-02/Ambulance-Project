import networkx as nx
import math
import requests
from algorithms.utility import haversine_distance, get_route_from_osrm

def create_graph_with_weights(ambulance_loc, hospitals, emergency_level):
    """Create a weighted graph based on locations and emergency level"""
    G = nx.Graph()
    
    # Add ambulance node
    ambulance_node = 'ambulance'
    G.add_node(ambulance_node, pos=(ambulance_loc['lat'], ambulance_loc['lng']))
    
    # Add hospital nodes with appropriate weights
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
            weight = weight / (hospital['priority'] + 0.5)
        elif emergency_level == 'medium':
            weight = weight / (hospital['priority'] * 0.3 + 0.7)
            
        # Adjust for capacity
        if hospital['capacity'] < 30:
            weight *= 1.2
            
        G.add_edge(ambulance_node, hospital_id, weight=weight)
    
    # Add edges between hospitals (fully connected graph)
    for i, hospital1 in enumerate(hospitals):
        for j, hospital2 in enumerate(hospitals):
            if i < j:  # Avoid duplicate edges
                hospital1_id = f"hospital_{i}"
                hospital2_id = f"hospital_{j}"
                
                # Calculate distance between hospitals
                distance = haversine_distance(
                    hospital1['lat'], hospital1['lng'],
                    hospital2['lat'], hospital2['lng']
                )
                
                G.add_edge(hospital1_id, hospital2_id, weight=distance)
    
    return G

def calculate_mst_prim(ambulance_loc, hospitals, emergency_level):
    """Calculate MST using Prim's algorithm and select best hospital"""
    G = create_graph_with_weights(ambulance_loc, hospitals, emergency_level)
    
    # Calculate MST using Prim's algorithm
    mst = nx.minimum_spanning_tree(G, algorithm='prim')
    
    # Find the closest hospital in the MST
    ambulance_node = 'ambulance'
    connected_hospitals = list(mst.neighbors(ambulance_node))
    
    if not connected_hospitals:
        # Fallback if no hospital is connected directly in MST
        return calculate_fallback_route(ambulance_loc, hospitals, emergency_level)
    
    # Find the hospital with the smallest weight (distance)
    best_hospital_id = min(
        connected_hospitals,
        key=lambda x: mst[ambulance_node][x]['weight']
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
        'algorithm': 'Prim\'s MST'
    }

def calculate_mst_kruskal(ambulance_loc, hospitals, emergency_level):
    """Calculate MST using Kruskal's algorithm and select best hospital"""
    G = create_graph_with_weights(ambulance_loc, hospitals, emergency_level)
    
    # Calculate MST using Kruskal's algorithm
    mst = nx.minimum_spanning_tree(G, algorithm='kruskal')
    
    # Find the closest hospital in the MST
    ambulance_node = 'ambulance'
    connected_hospitals = list(mst.neighbors(ambulance_node))
    
    if not connected_hospitals:
        # Fallback if no hospital is connected directly in MST
        return calculate_fallback_route(ambulance_loc, hospitals, emergency_level)
    
    # Find the hospital with the smallest weight (distance)
    best_hospital_id = min(
        connected_hospitals,
        key=lambda x: mst[ambulance_node][x]['weight']
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
        'algorithm': 'Kruskal\'s MST'
    }

def calculate_fallback_route(ambulance_loc, hospitals, emergency_level):
    """Fallback method if MST doesn't have direct connection to ambulance"""
    # Find the closest hospital by straight-line distance
    closest_hospital = min(
        hospitals,
        key=lambda h: haversine_distance(
            ambulance_loc['lat'], ambulance_loc['lng'],
            h['lat'], h['lng']
        )
    )
    
    # Get the actual route using OSRM
    route = get_route_from_osrm(
        ambulance_loc['lat'], ambulance_loc['lng'],
        closest_hospital['lat'], closest_hospital['lng']
    )
    
    return {
        'hospital': closest_hospital,
        'distance': route['distance'],
        'duration': route['duration'],
        'route': route['geometry'],
        'algorithm': 'Direct distance (fallback)'
    }