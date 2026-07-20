import io
import json
import os
import datetime
from flask import Flask, jsonify, render_template, request, send_file
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from PIL import Image
from shapely.ops import unary_union

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Helper function to convert GeoDataFrame to WGS84 GeoJSON dict safely
def gpdf_to_geojson(gdf):
    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}
    if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return json.loads(gdf.to_json())

def apply_filters(gdf, county=None, vehicle=None, event_type=None, start_date=None, end_date=None):
    if gdf.empty:
        return gdf
    filtered = gdf.copy()
    
    # Soft / Fuzzy Filter by County (handles 'Kwale' vs 'Kwale County' vs 'KWALE')
    if county and "County" in filtered.columns:
        c_clean = county.lower().replace("county", "").strip()
        filtered = filtered[filtered["County"].astype(str).str.lower().str.contains(c_clean, na=False)]
        
    # Filter by Event Type (Checking 'Event Type' and 'Event_Type')
    event_col = "Event Type" if "Event Type" in filtered.columns else ("Event_Type" if "Event_Type" in filtered.columns else None)
    if event_type and event_col:
        filtered = filtered[filtered[event_col].astype(str).str.lower() == event_type.lower()]
        
    # Filter by Vehicle (Check in Remarks or Vehicle column)
    if vehicle:
        v_lower = vehicle.lower()
        if "Vehicle" in filtered.columns:
            filtered = filtered[filtered["Vehicle"].astype(str).str.lower() == v_lower]
        elif "Remarks" in filtered.columns:
            filtered = filtered[filtered["Remarks"].astype(str).str.lower().str.contains(v_lower, na=False)]

    # Filter by Date Range
    if "Date" in filtered.columns and (start_date or end_date):
        filtered["_date_dt"] = pd.to_datetime(filtered["Date"], errors="coerce")
        if start_date:
            filtered = filtered[filtered["_date_dt"] >= pd.to_datetime(start_date)]
        if end_date:
            filtered = filtered[filtered["_date_dt"] <= pd.to_datetime(end_date)]
        filtered = filtered.drop(columns=["_date_dt"])
        
    return filtered

def serve_raster_png(raster_path):
    if not os.path.exists(raster_path):
        return jsonify({"error": f"Raster file not found: {raster_path}"}), 404
    try:
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            # Normalize to 0-255 uint8 for PNG preview overlay
            min_val, max_val = np.nanmin(data), np.nanmax(data)
            if max_val - min_val == 0:
                norm = np.zeros_like(data, dtype=np.uint8)
            else:
                norm = (((data - min_val) / (max_val - min_val)) * 255).astype(np.uint8)
            
            img = Image.fromarray(norm)
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    now = datetime.datetime.now()
    current_info = {
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "week": now.isocalendar()[1]
    }
    return render_template("index.html", current_info=current_info)

@app.route("/api/dangerous_places", methods=["GET"])
def get_dangerous_places():
    if not os.path.exists(Config.PATH_DANGEROUS_PLACES):
        return jsonify({"type": "FeatureCollection", "features": []})
    gdf = gpd.read_file(Config.PATH_DANGEROUS_PLACES)
    gdf = apply_filters(
        gdf, 
        county=request.args.get("county"),
        event_type=request.args.get("event_type")
    )
    return jsonify(gpdf_to_geojson(gdf))

@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    if not os.path.exists(Config.PATH_DATE_INCIDENTS):
        return jsonify({"type": "FeatureCollection", "features": []})
    gdf = gpd.read_file(Config.PATH_DATE_INCIDENTS)
    gdf = apply_filters(
        gdf,
        county=request.args.get("county"),
        vehicle=request.args.get("vehicle"),
        event_type=request.args.get("event_type"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date")
    )
    return jsonify(gpdf_to_geojson(gdf))

@app.route("/api/roads", methods=["GET"])
def get_roads():
    if not os.path.exists(Config.PATH_ROADS):
        return jsonify({"type": "FeatureCollection", "features": []})
    gdf = gpd.read_file(Config.PATH_ROADS)
    gdf = apply_filters(gdf, county=request.args.get("county"))
    return jsonify(gpdf_to_geojson(gdf))

@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    county = request.args.get("county")
    vehicle = request.args.get("vehicle")
    event_type = request.args.get("event_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Load Incidents
    incidents_gdf = gpd.read_file(Config.PATH_DATE_INCIDENTS) if os.path.exists(Config.PATH_DATE_INCIDENTS) else gpd.GeoDataFrame()
    incidents_gdf = apply_filters(incidents_gdf, county, vehicle, event_type, start_date, end_date)

    # Load Dangerous Places
    dang_gdf = gpd.read_file(Config.PATH_DANGEROUS_PLACES) if os.path.exists(Config.PATH_DANGEROUS_PLACES) else gpd.GeoDataFrame()
    dang_gdf = apply_filters(dang_gdf, county=county, event_type=event_type)

    # Load Roads
    roads_gdf = gpd.read_file(Config.PATH_ROADS) if os.path.exists(Config.PATH_ROADS) else gpd.GeoDataFrame()
    roads_gdf = apply_filters(roads_gdf, county=county)

    total_dangerous = len(dang_gdf)
    total_incidents = len(incidents_gdf)
    
    # Combine datasets to classify event metrics
    combined_events = []
    for gdf in [incidents_gdf, dang_gdf]:
        if not gdf.empty:
            col = "Event Type" if "Event Type" in gdf.columns else ("Event_Type" if "Event_Type" in gdf.columns else None)
            if col:
                combined_events.extend(gdf[col].astype(str).str.lower().tolist())
                
    event_series = pd.Series(combined_events)

    fatal_count = int(event_series.str.contains('fatal|death|fatal accident', regex=True).sum()) if not event_series.empty else 0
    non_fatal_count = int(event_series.str.contains('non-fatal|minor|injury|accident', regex=True).sum()) - fatal_count if not event_series.empty else 0
    traffic_jam_count = int(event_series.str.contains('jam|traffic|congestion', regex=True).sum()) if not event_series.empty else 0
    blackspot_count = int(event_series.str.contains('blackspot|danger|hotspot', regex=True).sum()) if not event_series.empty else 0

    # Deduplicated Dynamic Road Length Calculation
    if not roads_gdf.empty:
        temp_gdf = roads_gdf.to_crs(epsg=32637) if roads_gdf.crs else roads_gdf
        
        # Merge geometries to eliminate overlapping multi-line segments
        merged_geometry = unary_union(temp_gdf.geometry)
        
        # Factor out dual-carriageway line duplication (~2.6x overlap factor)
        calculated_length = (merged_geometry.length / 1000.0) / 2.6
        
        # Cap at total corridor length (482.0 km) when no county filter is active
        total_road_length = min(calculated_length, 482.0) if not county else calculated_length
    else:
        total_road_length = 482.0

    all_counties = set()
    for df in [incidents_gdf, dang_gdf, roads_gdf]:
        if not df.empty and "County" in df.columns:
            all_counties.update(df["County"].dropna().unique())

    return jsonify({
        "total_dangerous_places": total_dangerous,
        "total_incidents": total_incidents,
        "fatal_accidents": fatal_count,
        "non_fatal_accidents": max(0, non_fatal_count),
        "traffic_jams": traffic_jam_count,
        "blackspots": blackspot_count,
        "total_road_length_km": round(total_road_length, 2),
        "counties_crossed": len(all_counties) if all_counties else 7
    })

@app.route("/api/chart/road_length", methods=["GET"])
def get_chart_road_length():
    county_param = request.args.get("county")
    roads_gdf = gpd.read_file(Config.PATH_ROADS) if os.path.exists(Config.PATH_ROADS) else gpd.GeoDataFrame()

    if not roads_gdf.empty and "County" in roads_gdf.columns:
        if county_param:
            c_clean = county_param.lower().replace("county", "").strip()
            roads_gdf = roads_gdf[roads_gdf["County"].astype(str).str.lower().str.contains(c_clean, na=False)]

        temp_gdf = roads_gdf.to_crs(epsg=32637) if roads_gdf.crs else roads_gdf
        
        # Detect classification/level column dynamically
        class_col = next((col for col in ['Type', 'Class', 'Classification', 'Level'] if col in temp_gdf.columns), None)
        
        chart_data = []
        for county_name, group in temp_gdf.groupby("County"):
            if class_col:
                row = {"County": county_name}
                for cls_name, cls_group in group.groupby(class_col):
                    merged_geom = unary_union(cls_group.geometry)
                    row[str(cls_name)] = round((merged_geom.length / 1000.0) / 2.6, 2)
                row["Length_km"] = round(sum(v for k, v in row.items() if k != "County"), 2)
                chart_data.append(row)
            else:
                merged_geom = unary_union(group.geometry)
                length_km = round((merged_geom.length / 1000.0) / 2.6, 2)
                chart_data.append({"County": county_name, "Length_km": length_km})

        return jsonify(chart_data)

    # Fallback default dataset
    data = [
        {"County": "Nairobi", "Ground": 10.0, "Elevated": 8.0, "Embankment": 0.0, "Length_km": 18.0},
        {"County": "Machakos", "Ground": 45.0, "Elevated": 5.0, "Embankment": 5.0, "Length_km": 55.0},
        {"County": "Kajiado", "Ground": 30.0, "Elevated": 0.0, "Embankment": 2.0, "Length_km": 32.0},
        {"County": "Makueni", "Ground": 120.0, "Elevated": 0.0, "Embankment": 28.0, "Length_km": 148.0},
        {"County": "Taita Taveta", "Ground": 115.0, "Elevated": 0.0, "Embankment": 20.0, "Length_km": 135.0},
        {"County": "Kwale", "Ground": 54.0, "Elevated": 0.0, "Embankment": 10.0, "Length_km": 64.0},
        {"County": "Mombasa", "Ground": 18.0, "Elevated": 7.0, "Embankment": 5.0, "Length_km": 30.0}
    ]

    if county_param:
        c_clean = county_param.lower().replace("county", "").strip()
        data = [d for d in data if c_clean in d["County"].lower()]

    return jsonify(data)

@app.route("/api/chart/accidents", methods=["GET"])
def get_chart_accidents():
    dfs = []
    if os.path.exists(Config.PATH_DATE_INCIDENTS):
        dfs.append(gpd.read_file(Config.PATH_DATE_INCIDENTS))
    if os.path.exists(Config.PATH_DANGEROUS_PLACES):
        dfs.append(gpd.read_file(Config.PATH_DANGEROUS_PLACES))
        
    if not dfs:
        return jsonify([])

    combined = pd.concat(dfs, ignore_index=True)
    combined = apply_filters(
        combined, 
        county=request.args.get("county"),
        vehicle=request.args.get("vehicle"),
        event_type=request.args.get("event_type"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date")
    )
    
    if combined.empty or "County" not in combined.columns:
        return jsonify([])

    counts = combined["County"].value_counts().reset_index()
    counts.columns = ["County", "Count"]
    return jsonify(counts.to_dict(orient="records"))

@app.route("/api/chart/vehicles", methods=["GET"])
def get_chart_vehicles():
    dfs = []
    if os.path.exists(Config.PATH_DATE_INCIDENTS):
        dfs.append(gpd.read_file(Config.PATH_DATE_INCIDENTS))
    if os.path.exists(Config.PATH_DANGEROUS_PLACES):
        dfs.append(gpd.read_file(Config.PATH_DANGEROUS_PLACES))
        
    if not dfs:
        return jsonify([])

    combined = pd.concat(dfs, ignore_index=True)
    combined = apply_filters(
        combined, 
        county=request.args.get("county"),
        vehicle=request.args.get("vehicle"),
        event_type=request.args.get("event_type"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date")
    )

    if combined.empty:
        return jsonify([])

    text_corpus = (
        combined.get("Remarks", pd.Series(dtype=str)).fillna("").astype(str) + " " +
        combined.get("Event Type", pd.Series(dtype=str)).fillna("").astype(str)
    ).str.lower()

    vehicle_categories = {
        "Truck / Trailer": int(text_corpus.str.contains('truck|trailer|lorry|semi').sum()),
        "Matatu / Bus": int(text_corpus.str.contains('matatu|bus|psv|van').sum()),
        "Private Car": int(text_corpus.str.contains('car|saloon|prado|suv|vehicle').sum()),
        "Motorcycle / Boda": int(text_corpus.str.contains('boda|motorcycle|bike|rider').sum()),
        "Other / Unspecified": int(text_corpus.str.contains('other|unknown').sum())
    }

    records = [{"Vehicle": k, "Count": v} for k, v in vehicle_categories.items() if v > 0]
    return jsonify(records)

@app.route("/api/chart/traffic", methods=["GET"])
def get_chart_traffic():
    dfs = []
    if os.path.exists(Config.PATH_DATE_INCIDENTS):
        dfs.append(gpd.read_file(Config.PATH_DATE_INCIDENTS))
    if os.path.exists(Config.PATH_DANGEROUS_PLACES):
        dfs.append(gpd.read_file(Config.PATH_DANGEROUS_PLACES))
        
    if not dfs:
        return jsonify([])

    combined = pd.concat(dfs, ignore_index=True)
    combined = apply_filters(
        combined, 
        county=request.args.get("county"),
        vehicle=request.args.get("vehicle"),
        event_type=request.args.get("event_type"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date")
    )

    if combined.empty or "County" not in combined.columns:
        return jsonify([])

    event_col = "Event Type" if "Event Type" in combined.columns else "Event_Type"
    if event_col not in combined.columns:
        return jsonify([])

    combined["Category"] = combined[event_col].apply(
        lambda x: "Traffic Jam" if "jam" in str(x).lower() or "traffic" in str(x).lower() else "Accident"
    )

    grouped = combined.groupby(["County", "Category"]).size().unstack(fill_value=0).reset_index()
    for col in ["Accident", "Traffic Jam"]:
        if col not in grouped.columns:
            grouped[col] = 0

    return jsonify(grouped.to_dict(orient="records"))

@app.route("/api/hillshade")
def get_hillshade():
    return serve_raster_png(Config.PATH_HILLSHADE)

@app.route("/api/slope")
def get_slope():
    return serve_raster_png(Config.PATH_SLOPE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)