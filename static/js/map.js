/**
 * Map Initialization and GeoJSON Management
 */
let map;
let geojsonDangerousLayer;
let geojsonIncidentsLayer;
let geojsonRoadsLayer;
let hillshadeRasterLayer;
let slopeRasterLayer;

const MapModule = {
    init: function () {
        // Center along A109 corridor
        map = L.map('map').setView([-2.2, 37.9], 7);

        // Base Maps
        const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        const satellite = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            maxZoom: 19,
            attribution: '© Google Satellite'
        });

        const baseMaps = {
            "OpenStreetMap": osm,
            "Google Satellite": satellite
        };

        L.control.layers(baseMaps, null, { position: 'topright' }).addTo(map);
        L.control.scale({ imperial: false }).addTo(map);

        // Mouse Coordinates Handler
        map.on('mousemove', function (e) {
            document.getElementById('mouseCoordinates').innerText = 
                `Lat: ${e.latlng.lat.toFixed(4)}, Lon: ${e.latlng.lng.toFixed(4)}`;
        });

        this.initRasterLayers();
    },

    initRasterLayers: function () {
        // Bounds for overlay (Approx corridor bounds)
        const bounds = [[-4.1, 36.6], [-1.2, 39.7]];
        hillshadeRasterLayer = L.imageOverlay('/api/hillshade', bounds, { opacity: 0.5 });
        slopeRasterLayer = L.imageOverlay('/api/slope', bounds, { opacity: 0.5 });
    },

    loadLayers: function (params = "") {
        if (geojsonDangerousLayer) map.removeLayer(geojsonDangerousLayer);
        if (geojsonIncidentsLayer) map.removeLayer(geojsonIncidentsLayer);
        if (geojsonRoadsLayer) map.removeLayer(geojsonRoadsLayer);

        // Fetch Roads
        fetch(`/api/roads${params}`)
            .then(res => res.json())
            .then(data => {
                geojsonRoadsLayer = L.geoJSON(data, {
                    style: LayerManager.getRoadStyle,
                    onEachFeature: function (feature, layer) {
                        layer.bindPopup(PopupHandler.createFeaturePopup(feature.properties));
                    }
                });
                if (document.getElementById('layerRoads').checked) {
                    geojsonRoadsLayer.addTo(map);
                }
            });

        // Fetch Dangerous Places
        fetch(`/api/dangerous_places${params}`)
            .then(res => res.json())
            .then(data => {
                geojsonDangerousLayer = L.geoJSON(data, {
                    pointToLayer: LayerManager.getPointMarker,
                    onEachFeature: function (feature, layer) {
                        layer.bindPopup(PopupHandler.createFeaturePopup(feature.properties));
                    }
                });
                if (document.getElementById('layerDangerous').checked) {
                    geojsonDangerousLayer.addTo(map);
                }
            });

        // Fetch Incidents
        fetch(`/api/incidents${params}`)
            .then(res => res.json())
            .then(data => {
                geojsonIncidentsLayer = L.geoJSON(data, {
                    pointToLayer: LayerManager.getPointMarker,
                    onEachFeature: function (feature, layer) {
                        layer.bindPopup(PopupHandler.createFeaturePopup(feature.properties));
                    }
                });
                if (document.getElementById('layerIncidents').checked) {
                    geojsonIncidentsLayer.addTo(map);
                }
            });
    },

    toggleLayer: function (layerName, isChecked) {
        if (layerName === 'dangerous' && geojsonDangerousLayer) {
            isChecked ? map.addLayer(geojsonDangerousLayer) : map.removeLayer(geojsonDangerousLayer);
        } else if (layerName === 'incidents' && geojsonIncidentsLayer) {
            isChecked ? map.addLayer(geojsonIncidentsLayer) : map.removeLayer(geojsonIncidentsLayer);
        } else if (layerName === 'roads' && geojsonRoadsLayer) {
            isChecked ? map.addLayer(geojsonRoadsLayer) : map.removeLayer(geojsonRoadsLayer);
        } else if (layerName === 'hillshade') {
            isChecked ? map.addLayer(hillshadeRasterLayer) : map.removeLayer(hillshadeRasterLayer);
        } else if (layerName === 'slope') {
            isChecked ? map.addLayer(slopeRasterLayer) : map.removeLayer(slopeRasterLayer);
        }
    }
};