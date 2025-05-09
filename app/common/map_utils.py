"""Map utilities for processing GIS data and creating VIKTOR map features."""

import contextlib
import math
import os

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon

from viktor.core import Color
from viktor.errors import UserError
from viktor.views import MapFeature, MapPoint, MapPolygon


def validate_shapefile_exists(shapefile_path: str) -> None:
    """
    Validates that a shapefile exists at the specified path.

    Args:
        shapefile_path: Path to check

    Raises:
        UserError: If the file doesn't exist

    """
    if not os.path.exists(shapefile_path):
        raise UserError(f"Shapefile niet gevonden op verwachtte locatie: {shapefile_path}")


def validate_gdf_crs(gdf: gpd.GeoDataFrame) -> None:
    """
    Validates that a GeoDataFrame has a valid Coordinate Reference System.

    Args:
        gdf: GeoDataFrame to validate

    Raises:
        UserError: If the GeoDataFrame has no CRS

    """
    if gdf.crs is None:
        raise UserError("Shapefile mist een Coordinate Reference System (.prj bestand).")


def validate_gdf_columns(gdf: gpd.GeoDataFrame, required_columns: list[str] | None = None) -> None:
    """
    Validates that a GeoDataFrame has required columns.

    Args:
        gdf: GeoDataFrame to validate
        required_columns: List of required column names (defaults to ["OBJECTNUMM"])

    Raises:
        UserError: If any required column is missing

    """
    if required_columns is None:
        required_columns = ["OBJECTNUMM"]

    for column in required_columns:
        if column not in gdf.columns:
            raise UserError(f"Shapefile mist de kolom '{column}'.")


def load_and_prepare_shapefile(shapefile_path: str, allowed_objectnumm: set[str]) -> gpd.GeoDataFrame | None:
    """
    Loads a shapefile, filters by allowed OBJECTNUMM values, and ensures correct CRS.

    Args:
        shapefile_path: Path to the shapefile (.shp)
        allowed_objectnumm: Set of OBJECTNUMM values to filter for

    Returns:
        Filtered GeoDataFrame or None if no matches found

    Raises:
        UserError: If the shapefile is invalid, missing, or doesn't have required data

    """
    try:
        gdf = gpd.read_file(shapefile_path)

        # Ensure the CRS is WGS84 (EPSG:4326)
        validate_gdf_crs(gdf)
        if gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # Filter based on OBJECTNUMM
        validate_gdf_columns(gdf)
        filtered_gdf = gdf[gdf["OBJECTNUMM"].astype(str).isin([str(x) for x in allowed_objectnumm])]

        if filtered_gdf.empty:
            return None  # Return None if no allowed bridges found in shapefile
        return filtered_gdf  # noqa: TRY300

    except FileNotFoundError:
        # Specific error if components (.shx, .dbf) are missing relative to .shp
        raise UserError(f"Kon shapefile componenten niet vinden nabij {shapefile_path}. Zorg dat .shp, .shx, .dbf, .prj aanwezig zijn.")
    except ImportError:
        raise UserError("GeoPandas is niet correct geïnstalleerd.")
    except Exception as e:
        raise UserError(f"Fout bij het verwerken van {shapefile_path}: {e}")


def create_map_polygon_feature(polygon: Polygon, description: str, color: Color = Color.blue()) -> MapPolygon | None:
    """
    Creates a MapPolygon feature from a Shapely Polygon, handling invalid coordinates.

    Args:
        polygon: The shapely Polygon geometry
        description: Text description for the polygon
        color: Color for the polygon (defaults to blue)

    Returns:
        MapPolygon feature if successful, None if invalid

    """
    raw_coords = list(polygon.exterior.coords)
    valid_coords = [(lat, lon) for lon, lat in raw_coords if math.isfinite(lat) and math.isfinite(lon)]
    map_points = [MapPoint(lat, lon) for lat, lon in valid_coords]

    if len(map_points) >= 3:  # A polygon needs at least 3 points
        with contextlib.suppress(Exception):  # Ignore potential VIKTOR errors creating the polygon
            return MapPolygon(map_points, description=description, color=color)
    return None


def process_bridge_geometries(
    gdf_row: gpd.GeoSeries, object_number: str, bridge_name: str | None = None, color: Color = Color.blue()
) -> tuple[list[MapFeature], MapPoint | None]:
    """
    Processes a bridge's geometry from a GeoDataFrame row into MapFeatures.

    Args:
        gdf_row: Row from a GeoDataFrame containing geometry and attributes
        object_number: The bridge's object number identifier
        bridge_name: Optional name of the bridge
        color: Color for the map features (defaults to blue)

    Returns:
        Tuple of (list of map features, error point or None)

    """
    features: list[MapFeature] = []

    try:
        geom = gdf_row.geometry
        objectnaam_shp = gdf_row.get("OBJECTNAAM", "")

        # Format description
        if bridge_name and isinstance(bridge_name, str) and bridge_name.strip():
            description = f"{object_number} - {bridge_name}"
        elif objectnaam_shp and isinstance(objectnaam_shp, str) and objectnaam_shp.strip():
            description = f"{object_number} - {objectnaam_shp.strip()}"
        else:
            description = str(object_number)

        if isinstance(geom, Polygon):
            feature = create_map_polygon_feature(geom, description, color)
            if feature:
                features.append(feature)
        elif isinstance(geom, MultiPolygon):
            for i, poly_part in enumerate(geom.geoms):
                part_description = f"{description} (deel {i + 1})"
                feature = create_map_polygon_feature(poly_part, part_description, color)
                if feature:
                    features.append(feature)

        if not features:
            return [], MapPoint(52.37, 4.89, description=f"Geen geldige geometrie gevonden voor brug '{object_number}'.")
        return features, None  # noqa: TRY300
    except Exception as e:
        return [], MapPoint(52.37, 4.89, description=f"Fout bij geometrie verwerking: {e}")


def process_all_bridges_geometries(gdf: gpd.GeoDataFrame, color: Color = Color.red()) -> list[MapFeature]:
    """
    Processes all bridge geometries from a GeoDataFrame to create MapFeatures.

    Args:
        gdf: GeoDataFrame containing bridge geometries and attributes
        color: Color for the map features (defaults to red)

    Returns:
        List of map features for all bridges

    """
    features = []
    for _index, bridge in gdf.iterrows():
        object_nummer = bridge.get("OBJECTNUMM")
        if not object_nummer:
            continue

        bridge_features, _error = process_bridge_geometries(bridge, str(object_nummer), color=color)
        features.extend(bridge_features)

    return features
