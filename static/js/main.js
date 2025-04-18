// Modified JavaScript code with updated hospital and ambulance icons
// Updated to replace Dijkstra with TSP

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map centered at Coimbatore
    const map = L.map('map').setView([11.0168, 76.9558], 13);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Global variables
    let hospitals = [];
    let ambulanceMarker = null;
    let routingControl = null;
    let activeHospitalMarkers = [];
    let hospitalMarkers = {};

    // Hospital icon (blue location pin)
    const hospitalIcon = L.icon({
        iconUrl: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });

    // Ambulance icon (red location pin)
    const ambulanceIcon = L.icon({
        iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });

    fetch('/api/hospitals')
        .then(response => response.json())
        .then(data => {
            hospitals = data;
            initializeHospitals(hospitals);
        })
        .catch(error => console.error('Error fetching hospitals:', error));

    function initializeHospitals(hospitals) {
        const hospitalCardsContainer = document.getElementById('hospital-cards');
        hospitalCardsContainer.innerHTML = '';

        hospitals.forEach((hospital, index) => {
            const marker = L.marker([hospital.lat, hospital.lng], {
                icon: hospitalIcon
            }).addTo(map);

            marker.bindPopup(`
                <strong>${hospital.name}</strong><br>
                Priority: ${hospital.priority}/5<br>
                Capacity: ${hospital.capacity}%<br>
                <button class="popup-select-btn" data-hospital-index="${index}">Select</button>
            `);

            hospitalMarkers[index] = marker;

            const template = document.getElementById('hospital-card-template');
            const cardClone = document.importNode(template.content, true);

            cardClone.querySelector('.hospital-name').textContent = hospital.name;
            cardClone.querySelector('.hospital-address').textContent = hospital.address;
            cardClone.querySelector('.priority-level').textContent = `${hospital.priority}/5`;
            cardClone.querySelector('.capacity-level').textContent = `${hospital.capacity}%`;

            const selectBtn = cardClone.querySelector('.select-hospital-btn');
            selectBtn.dataset.hospitalIndex = index;
            selectBtn.addEventListener('click', function() {
                const hospitalIndex = parseInt(this.dataset.hospitalIndex);
                selectHospital(hospitalIndex);
            });

            hospitalCardsContainer.appendChild(cardClone);
        });

        document.addEventListener('click', function(e) {
            if (e.target && e.target.className === 'popup-select-btn') {
                const hospitalIndex = parseInt(e.target.dataset.hospitalIndex);
                selectHospital(hospitalIndex);
            }
        });
    }

    map.on('click', function(e) {
        setAmbulanceLocation(e.latlng);
    });

    function setAmbulanceLocation(latlng) {
        if (ambulanceMarker) {
            map.removeLayer(ambulanceMarker);
        }

        ambulanceMarker = L.marker(latlng, {
            icon: ambulanceIcon,
            draggable: true
        }).addTo(map);

        ambulanceMarker.bindPopup("Ambulance Location<br>Drag to adjust").openPopup();

        document.getElementById('route-info').innerHTML = '<p>Ambulance location set. Select an algorithm and calculate route.</p>';

        document.getElementById('calculate-btn').disabled = false;
        document.getElementById('compare-btn').disabled = false;

        ambulanceMarker.on('dragend', function() {
            clearRoute();
        });
    }

    function selectHospital(hospitalIndex) {
        if (!ambulanceMarker) {
            alert('Please set ambulance location first by clicking on the map.');
            return;
        }

        const hospital = hospitals[hospitalIndex];
        calculateAndDisplayRoute(hospital);
    }

    document.getElementById('calculate-btn').addEventListener('click', function() {
        if (!ambulanceMarker) {
            alert('Please set ambulance location first by clicking on the map.');
            return;
        }

        const algorithm = document.getElementById('algorithm-select').value;
        const emergencyLevel = document.getElementById('emergency-level').value;

        const ambulanceLoc = {
            lat: ambulanceMarker.getLatLng().lat,
            lng: ambulanceMarker.getLatLng().lng
        };

        const requestData = {
            ambulance: ambulanceLoc,
            emergency_level: emergencyLevel
        };

        let endpoint = '';
        if (algorithm === 'tsp') {  // Updated from 'dijkstra' to 'tsp'
            endpoint = '/api/tsp';  // Updated endpoint
        } else if (algorithm.startsWith('mst')) {
            endpoint = '/api/mst';
            requestData.algorithm = algorithm.split('-')[1];
        } else if (algorithm === 'multistage') {
            endpoint = '/api/multistage';
        }

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            displayRoute(data);
        })
        .catch(error => {
            console.error('Error calculating route:', error);
            document.getElementById('route-info').innerHTML = '<p class="error">Error calculating route. Please try again.</p>';
        });
    });

    document.getElementById('compare-btn').addEventListener('click', function() {
        if (!ambulanceMarker) {
            alert('Please set ambulance location first by clicking on the map.');
            return;
        }

        const emergencyLevel = document.getElementById('emergency-level').value;

        const ambulanceLoc = {
            lat: ambulanceMarker.getLatLng().lat,
            lng: ambulanceMarker.getLatLng().lng
        };

        const requestData = {
            ambulance: ambulanceLoc,
            emergency_level: emergencyLevel
        };

        fetch('/api/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            displayComparisonResults(data);
        })
        .catch(error => {
            console.error('Error comparing algorithms:', error);
            document.getElementById('route-info').innerHTML = '<p class="error">Error comparing algorithms. Please try again.</p>';
        });
    });

    document.getElementById('clear-ambulance-btn').addEventListener('click', function() {
        clearAmbulance();
        clearRoute();
        document.getElementById('route-info').innerHTML = '<p>Click on the map to set ambulance location.</p>';
    });

    function clearAmbulance() {
        if (ambulanceMarker) {
            map.removeLayer(ambulanceMarker);
            ambulanceMarker = null;
        }
    }

    function clearRoute() {
        if (routingControl) {
            map.removeControl(routingControl);
            routingControl = null;
        }

        for (const index in hospitalMarkers) {
            hospitalMarkers[index].setIcon(hospitalIcon);
        }
    }

    function displayRoute(routeData) {
        clearRoute();

        const hospital = routeData.hospital;
        const algorithm = routeData.algorithm || document.getElementById('algorithm-select').value;

        const hospitalIndex = hospitals.findIndex(h => h.name === hospital.name);
        if (hospitalIndex !== -1 && hospitalMarkers[hospitalIndex]) {
            hospitalMarkers[hospitalIndex].setIcon(hospitalIcon);
            hospitalMarkers[hospitalIndex].openPopup();
        }

        const waypoints = [
            L.latLng(ambulanceMarker.getLatLng().lat, ambulanceMarker.getLatLng().lng),
            L.latLng(hospital.lat, hospital.lng)
        ];

        routingControl = L.Routing.control({
            waypoints: waypoints,
            routeWhileDragging: false,
            showAlternatives: false,
            fitSelectedRoutes: true,
            lineOptions: {
                styles: [{ color: '#0073FF', weight: 6 }]
            },
            createMarker: function() { return null; }
        }).addTo(map);

        const routeInfo = `
            <h4>Route Calculated with ${algorithm}</h4>
            <p><strong>Selected Hospital:</strong> ${hospital.name}</p>
            <p><strong>Distance:</strong> ${routeData.distance.toFixed(2)} km</p>
            <p><strong>Estimated Time:</strong> ${routeData.duration.toFixed(2)} minutes</p>
            <p><strong>Hospital Priority:</strong> ${hospital.priority}/5</p>
            <p><strong>Hospital Capacity:</strong> ${hospital.capacity}%</p>
        `;

        document.getElementById('route-info').innerHTML = routeInfo;
    }

    function displayComparisonResults(results) {
        clearRoute();

        let comparisonHtml = '<h4>Algorithm Comparison Results</h4>';
        comparisonHtml += '<table class="comparison-table">';
        comparisonHtml += `
            <tr>
                <th>Algorithm</th>
                <th>Hospital</th>
                <th>Distance (km)</th>
                <th>Time (min)</th>
            </tr>
        `;

        for (const algorithm in results) {
            const result = results[algorithm];
            comparisonHtml += `
                <tr class="algorithm-row" data-algorithm="${algorithm}">
                    <td>${algorithm}</td>
                    <td>${result.hospital.name}</td>
                    <td>${result.distance.toFixed(2)}</td>
                    <td>${result.duration.toFixed(2)}</td>
                </tr>
            `;
        }

        comparisonHtml += '</table>';
        comparisonHtml += '<p>Click on a row to view the route.</p>';

        document.getElementById('route-info').innerHTML = comparisonHtml;

        document.querySelectorAll('.algorithm-row').forEach(row => {
            row.addEventListener('click', function() {
                const algorithm = this.dataset.algorithm;
                displayRoute(results[algorithm]);
            });
        });
    }

    function calculateAndDisplayRoute(hospital) {
        if (!ambulanceMarker) {
            alert('Please set ambulance location first by clicking on the map.');
            return;
        }

        clearRoute();

        const ambulanceLoc = {
            lat: ambulanceMarker.getLatLng().lat,
            lng: ambulanceMarker.getLatLng().lng
        };

        const waypoints = [
            L.latLng(ambulanceLoc.lat, ambulanceLoc.lng),
            L.latLng(hospital.lat, hospital.lng)
        ];

        routingControl = L.Routing.control({
            waypoints: waypoints,
            routeWhileDragging: false,
            showAlternatives: false,
            lineOptions: {
                styles: [{ color: '#0073FF', weight: 6 }]
            },
            createMarker: function() { return null; }
        }).addTo(map);

        const hospitalIndex = hospitals.findIndex(h => h.name === hospital.name);
        if (hospitalIndex !== -1 && hospitalMarkers[hospitalIndex]) {
            hospitalMarkers[hospitalIndex].setIcon(hospitalIcon);
            hospitalMarkers[hospitalIndex].openPopup();
        }

        document.getElementById('route-info').innerHTML = `
            <h4>Manual Selection</h4>
            <p><strong>Selected Hospital:</strong> ${hospital.name}</p>
            <p><strong>Hospital Priority:</strong> ${hospital.priority}/5</p>
            <p><strong>Hospital Capacity:</strong> ${hospital.capacity}%</p>
            <p>Route distance and time will be calculated...</p>
        `;
    }
});