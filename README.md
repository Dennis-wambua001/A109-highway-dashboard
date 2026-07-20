# A109 Nairobi–Mombasa Highway Road Safety Intelligence Dashboard

A full-stack Web GIS Application designed for highway road safety decision support, terrain analysis, and traffic congestion management along Kenya's primary economic corridor (A109).

## Features
- **Spatial Map Layer Visualization:** Dynamic Leaflet rendering of dangerous places, incident locations, road classification lines, and terrain rasters (Hillshade & Slope).
- **Automated KPI Computation:** Backend GeoPandas spatial processing for real-time statistical aggregations.
- **Synchronized Visual Analytics:** Plotly.js charts updated dynamically based on active map filters.
- **Global Interactivity & Filtering:** Filter across counties, vehicle categories, and incident event types.

## Setup Instructions

1. Ensure spatial GeoPackage and GeoTIFF datasets exist inside the `data/` folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt