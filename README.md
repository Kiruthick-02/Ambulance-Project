# Shortest Path Ambulance Routing System

A full-stack web application that provides ambulance routing in Coimbatore, Tamil Nadu using multiple shortest path algorithms.

## Features

- Interactive map visualization using Leaflet.js and OpenStreetMap
- Real-time ambulance routing to the nearest hospital
- Multiple routing algorithms:
  - TSP Algorithm
  - MST with Prim's Algorithm
  - MST with Kruskal's Algorithm
  - Multistage Graph Algorithm
- Consideration of hospital priority and capacity
- Emergency level selection
- Algorithm comparison capability

## Tech Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML, CSS, JavaScript
- **Map**: Leaflet.js with OpenStreetMap
- **Routing**: OSRM (Open Source Routing Machine)
- **Graph Algorithms**: NetworkX library

## Hospital Data

The system includes data for 8 major hospitals in Coimbatore:
1. Kovai Medical Center and Hospital (KMCH)
2. PSG Hospitals
3. Sri Ramakrishna Hospital
4. G. Kuppuswamy Naidu Memorial Hospital
5. KG Hospital
6. Royal Care Super Speciality Hospital
7. Ganga Medical Centre & Hospitals
8. Coimbatore Medical College Hospital

## Project Structure

```
Ambulance-Routing-System/
├── app.py                 # Flask application entry point
├── static/                # Static files
│   ├── css/              
│   │   └── style.css     # CSS styles
│   ├── js/               
│   │   └── main.js       # Frontend JavaScript
│   └── img/              # Images (if any)
├── templates/            
│   └── index.html        # Main HTML template
├── algorithms/           # Algorithm implementations
│   ├── __init__.py      
│   ├── tsp.py            # TSP algorithm
│   ├── mst.py            # MST algorithms (Prim's and Kruskal's)
│   └── multistage.py     # Multistage graph algorithm
├── data/                
│   └── hospitals.json    # Hospital data
├── utils/               
│   ├── __init__.py      
│   └── map_utils.py      # Map utility functions
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ambulance-routing-system.git
   cd ambulance-routing-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Use

1. Click on the map to set the ambulance's current location
2. Select an algorithm from the dropdown
3. Choose an emergency level
4. Click "Calculate Route" to find the best hospital
5. Use "Compare All Algorithms" to view and compare different routing options
6. Click on a hospital card or marker to manually select a specific hospital

## License

This project is licensed under the MIT License.