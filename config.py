import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a109-road-safety-gis-secret-key-2026")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    
    # File Paths - Edit paths here only
    PATH_DANGEROUS_PLACES = os.path.join(DATA_DIR, "Dangerous places.gpkg")
    PATH_DATE_INCIDENTS = os.path.join(DATA_DIR, "date-based incidents.gpkg")
    PATH_ROADS = os.path.join(DATA_DIR, "roads.gpkg")
    PATH_HILLSHADE = os.path.join(DATA_DIR, "viz.hh_hillshade.tif")
    PATH_SLOPE = os.path.join(DATA_DIR, "viz.hh_slope.tif")