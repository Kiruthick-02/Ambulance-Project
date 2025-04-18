from flask import Flask, render_template, request, jsonify
import json
import os
from algorithms.tsp import calculate_tsp_route  # Updated import
from algorithms.mst import calculate_mst_prim, calculate_mst_kruskal
from algorithms.multistage import calculate_multistage_route

app = Flask(__name__)

# Load hospital data
with open('data/hospitals.json', 'r') as f:
    hospitals = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    return jsonify(hospitals)

@app.route('/api/tsp', methods=['POST'])  # Updated route
def tsp():  # Updated function name
    data = request.get_json()
    ambulance_loc = data['ambulance']
    emergency_level = data['emergency_level']
    
    result = calculate_tsp_route(ambulance_loc, hospitals, emergency_level)
    return jsonify(result)

@app.route('/api/mst', methods=['POST'])
def mst():
    data = request.get_json()
    ambulance_loc = data['ambulance']
    emergency_level = data['emergency_level']
    algorithm = data.get('algorithm', 'prim')  # Default to Prim's
    
    if algorithm == 'prim':
        result = calculate_mst_prim(ambulance_loc, hospitals, emergency_level)
    else:  # kruskal
        result = calculate_mst_kruskal(ambulance_loc, hospitals, emergency_level)
    
    return jsonify(result)

@app.route('/api/multistage', methods=['POST'])
def multistage():
    data = request.get_json()
    ambulance_loc = data['ambulance']
    emergency_level = data['emergency_level']
    
    result = calculate_multistage_route(ambulance_loc, hospitals, emergency_level)
    return jsonify(result)

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.get_json()
    ambulance_loc = data['ambulance']
    emergency_level = data['emergency_level']
    
    tsp_result = calculate_tsp_route(ambulance_loc, hospitals, emergency_level)  # Updated
    prim_result = calculate_mst_prim(ambulance_loc, hospitals, emergency_level)
    kruskal_result = calculate_mst_kruskal(ambulance_loc, hospitals, emergency_level)
    multistage_result = calculate_multistage_route(ambulance_loc, hospitals, emergency_level)
    
    return jsonify({
        'tsp': tsp_result,  # Updated
        'prim': prim_result,
        'kruskal': kruskal_result,
        'multistage': multistage_result
    })

if __name__ == '__main__':
    app.run(debug=True)