"""
Utilities for GIS data processing and visualization.

This module contains functions for loading and processing GIS data from shapefiles
for bridge visualization and analysis.
"""

from typing import Any

import geopandas as gpd


def load_bridge_shapefile(shapefile_path: str, filter_condition: dict[str, Any] | None = None) -> gpd.GeoDataFrame:
    """
    Load bridge data from a shapefile.

    :param shapefile_path: Path to the shapefile (.shp)
    :param filter_condition: Optional dictionary of column name and value pairs to filter the data
    :returns: GeoDataFrame containing bridge geometries and attributes
    :rtype: gpd.GeoDataFrame
    """
    # Load the shapefile
    gdf = gpd.read_file(shapefile_path)

    # Apply filter if provided
    if filter_condition:
        for column, value in filter_condition.items():
            gdf = gdf[gdf[column] == value]

    return gdf


def prepare_bridge_data_for_viktor(gdf: gpd.GeoDataFrame) -> list[dict[str, Any]]:
    """
    Convert GeoDataFrame to a format suitable for VIKTOR MapView.

    :param gdf: GeoDataFrame containing bridge geometries
    :returns: List of dictionaries with bridge data for VIKTOR MapView
    :rtype: List[Dict[str, Any]]
    """
    # Convert to WGS84 (EPSG:4326) which is required for VIKTOR MapView
    if gdf.crs and gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # List to store map features
    map_features = []

    # Process each bridge feature
    for idx, row in gdf.iterrows():
        # Extract geometry coordinates
        if row.geometry.type == "Point":
            coords = [(row.geometry.y, row.geometry.x)]
        elif row.geometry.type == "Polygon":
            # Convert polygon to list of (lat, lon) coordinates
            coords = [(y, x) for x, y in row.geometry.exterior.coords]
        elif row.geometry.type == "LineString":
            coords = [(y, x) for x, y in row.geometry.coords]
        elif row.geometry.type == "MultiPolygon":
            # Use the first polygon for simplicity
            coords = [(y, x) for x, y in row.geometry.geoms[0].exterior.coords]
        else:
            # Skip unsupported geometries
            continue

        # Create feature with attributes
        feature = {
            "coordinates": coords,
            "type": row.geometry.type.lower(),
            "properties": {col: str(val) for col, val in row.items() if col != "geometry"},
        }

        map_features.append(feature)

    return map_features


def get_map_center_and_zoom(gdf: gpd.GeoDataFrame) -> tuple[tuple[float, float], int]:
    """
    Calculate appropriate center coordinates and zoom level for the map.

    :param gdf: GeoDataFrame containing bridge geometries
    :returns: Tuple of center coordinates (lat, lon) and zoom level
    :rtype: Tuple[Tuple[float, float], int]
    """
    # Convert to WGS84 if needed
    if gdf.crs and gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Get bounds of all geometries
    bounds = gdf.total_bounds  # (minx, miny, maxx, maxy)

    # Calculate center
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2

    # Estimate zoom level based on bounding box size
    # This is a simple heuristic - might need tuning
    lon_diff = bounds[2] - bounds[0]
    zoom = 12  # Default zoom

    if lon_diff > 0.5:
        zoom = 10
    elif lon_diff > 0.1:
        zoom = 11
    elif lon_diff > 0.05:
        zoom = 12
    elif lon_diff > 0.01:
        zoom = 13
    else:
        zoom = 14

    return (center_lat, center_lon), zoom
