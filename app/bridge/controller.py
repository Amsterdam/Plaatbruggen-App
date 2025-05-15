"""Module for the Bridge entity controller."""

import os  # Add import for os

import geopandas as gpd  # Add import for geopandas
import plotly.graph_objects as go  # Import Plotly graph objects
import trimesh
import trimesh.transformations as tf
import numpy as np
from src.geometry.model_creator import create_axes
from src.geometry.longitudinal_section import create_longitudinal_section
from src.geometry.cross_section import create_cross_section_view
from src.geometry.horizontal_section import create_horizontal_section_view

import viktor.api_v1 as api_sdk  # Import VIKTOR API SDK
from app.common.map_utils import (
    process_bridge_geometries,
    validate_gdf_columns,
    validate_gdf_crs,
    validate_shapefile_exists,
)
from app.constants import (  # Replace relative imports with absolute imports
    OUTPUT_REPORT_PATH,
)
from src.geometry.model_creator import (
    create_2d_top_view,
    create_3d_model,
    create_cross_section,
)
from viktor.core import File, ViktorController
from viktor.errors import UserError  # Add UserError
from viktor.utils import convert_word_to_pdf
from viktor.views import (
    GeometryResult,
    GeometryView,
    MapPoint,  # Add MapPoint
    MapResult,  # Add MapResult
    MapView,  # Add MapView
    PDFResult,
    PDFView,
    PlotlyResult,  # Import PlotlyResult
    PlotlyView,  # Import PlotlyView
)

# Import parametrization from the separate file
from .parametrization import BridgeParametrization


class BridgeController(ViktorController):
    """Controller for the individual Bridge entity."""

    label = "Brug"
    parametrization = BridgeParametrization  # type: ignore[assignment]

    def _get_bridge_entity_data(self, entity_id: int) -> tuple[str | None, str | None, MapResult | None]:
        """Fetches bridge entity data (OBJECTNUMM and name) using the VIKTOR API."""
        if not entity_id:
            return None, None, MapResult([MapPoint(52.37, 4.89, description="Entity ID niet gevonden.")])
        try:
            viktor_api = api_sdk.API()
            current_entity = viktor_api.get_entity(entity_id)
            last_params = current_entity.last_saved_params
            info_page_params = last_params.get("info")

            objectnumm = info_page_params.bridge_objectnumm if info_page_params and hasattr(info_page_params, "bridge_objectnumm") else None
            name = info_page_params.bridge_name if info_page_params and hasattr(info_page_params, "bridge_name") else ""
            if objectnumm is None:
                return None, None, MapResult([MapPoint(52.37, 4.89, description="OBJECTNUMM van brug niet gevonden in opgeslagen parameters.")])
            # Using explicit else to satisfy linter
            return objectnumm, name, None  # noqa: TRY300
        except Exception as e:
            return None, None, MapResult([MapPoint(52.37, 4.89, description=f"Fout bij ophalen entity data: {e}")])

    def _get_shapefile_path(self) -> tuple[str | None, MapResult | None]:
        """Constructs and validates the path to the shapefile."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            resources_dir = os.path.join(current_dir, "..", "..", "resources")
            shapefile_path = os.path.join(resources_dir, "gis", "Bruggenkaart.shp")

            # Using a nested try/except with else to properly handle validation errors
            try:
                validate_shapefile_exists(shapefile_path)  # This might raise UserError
            except UserError as ue:
                return None, MapResult([MapPoint(52.37, 4.89, description=str(ue))])
            else:
                # Using explicit else to satisfy linter
                return shapefile_path, None  # Only reached if validation succeeds

        except Exception as e:
            return None, MapResult([MapPoint(52.37, 4.89, description=f"Fout bij bepalen bestandspaden: {e}")])

    def _load_and_filter_geodataframe(self, shapefile_path: str, objectnumm: str) -> tuple[gpd.GeoDataFrame | None, MapResult | None]:
        """Loads the shapefile, validates it, and filters for the specific bridge."""
        try:
            gdf = gpd.read_file(shapefile_path)
            validate_gdf_crs(gdf)  # Using shared utility function
            if gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)
            validate_gdf_columns(gdf)  # Using shared utility function

            target_bridge_gdf = gdf[gdf["OBJECTNUMM"].astype(str) == str(objectnumm)]
            if target_bridge_gdf.empty:
                return None, MapResult([MapPoint(52.37, 4.89, description=f"Brug met OBJECTNUMM '{objectnumm}' niet gevonden in shapefile.")])
            # Using explicit else to satisfy linter
            return target_bridge_gdf, None  # noqa: TRY300
        except UserError as ue:
            return None, MapResult([MapPoint(52.37, 4.89, description=str(ue))])
        except ImportError:
            return None, MapResult([MapPoint(52.37, 4.89, description="GeoPandas is niet correct geïnstalleerd.")])
        except Exception as e:
            return None, MapResult([MapPoint(52.37, 4.89, description=f"Fout bij verwerken shapefile: {e}")])

    @MapView("Locatie Brug", duration_guess=2)
    def get_bridge_map_view(self, params: BridgeParametrization, **kwargs) -> MapResult:  # noqa: ARG002, PLR0911
        """Displays the current bridge polygon from the shapefile in the resources folder."""
        entity_id = kwargs.get("entity_id")

        # Validate entity_id before proceeding
        if not isinstance(entity_id, int):
            return MapResult([MapPoint(52.37, 4.89, description="Ongeldige entity ID ontvangen.")])

        # Process pipeline with early returns only for errors
        current_objectnumm, bridge_name_from_params, error_result = self._get_bridge_entity_data(entity_id)
        if error_result:
            return error_result

        # Here we handle cases when objectnumm or bridge_name are None
        if current_objectnumm is None:
            return MapResult([MapPoint(52.37, 4.89, description="Interne fout: OBJECTNUMM onbekend na API call.")])

        if bridge_name_from_params is None:
            bridge_name_from_params = ""

        # Get shapefile path
        shapefile_path, error_result = self._get_shapefile_path()
        if error_result:
            return error_result

        if shapefile_path is None:
            return MapResult([MapPoint(52.37, 4.89, description="Interne fout: Shapefile pad onbekend.")])

        # Load and filter geodataframe
        target_bridge_gdf, error_result = self._load_and_filter_geodataframe(shapefile_path, current_objectnumm)
        if error_result:
            return error_result

        if target_bridge_gdf is None:
            return MapResult([MapPoint(52.37, 4.89, description="Interne fout: GeoDataFrame onbekend na laden.")])

        # Process bridge geometries using the utility function
        features, error_point = process_bridge_geometries(target_bridge_gdf.iloc[0], current_objectnumm, bridge_name_from_params)

        if error_point:
            return MapResult([error_point])

        # Success case
        return MapResult(features)

    # ============================================================================================================
    # input - Dimension
    # ============================================================================================================

    @GeometryView("3D Model", duration_guess=1, x_axis_to_right=False)
    def get_3d_view(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """Generates a 3D representation of the bridge deck."""
        combined_scene = create_3d_model(params)
        # Export the scene as a GLTF file and return it as a GeometryResult
        geometry = File()
        with geometry.open_binary() as w:
            w.write(trimesh.exchange.gltf.export_glb(combined_scene))
        return GeometryResult(geometry, geometry_type="gltf")

    @PlotlyView("Bovenaanzicht", duration_guess=1)
    def get_top_view(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002, C901
        """
        Generates a 2D top view of the bridge deck with dimensions.

        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            PlotlyResult: A 2D representation of the top view.

        """
        top_view_data = create_2d_top_view(params)

        bridge_lines = top_view_data.get("bridge_lines", [])
        zone_annotations_data = top_view_data.get("zone_annotations", [])
        dimension_lines_data = top_view_data.get("dimension_lines", [])
        dimension_texts_data = top_view_data.get("dimension_texts", [])
        cross_section_labels_data = top_view_data.get("cross_section_labels", [])
        zone_polygons_data = top_view_data.get("zone_polygons", [])

        fig = go.Figure()

        # Add zone background fills
        for poly in zone_polygons_data:
            vertices = poly.get("vertices", [])
            if vertices:
                x_coords = [v[0] for v in vertices] + [vertices[0][0]]
                y_coords = [v[1] for v in vertices] + [vertices[0][1]]
                fig.add_trace(
                    go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode="lines",
                        fill="toself",
                        fillcolor=poly.get("color", "rgba(128,128,128,0.1)"),
                        line={"width": 0},  # Use literal dict
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

        # Add bridge outline lines
        for line_segment in bridge_lines:
            fig.add_trace(
                go.Scatter(
                    x=[line_segment["start"][0], line_segment["end"][0]],
                    y=[line_segment["start"][1], line_segment["end"][1]],
                    mode="lines",
                    line={"color": "blue", "width": 2},  # Use literal dict
                    hoverinfo="none",
                )
            )

        # Add dimension lines (this loop does nothing as dimension_lines_data is empty)
        for dim_line in dimension_lines_data:
            line_props = {"color": "red", "width": 1}  # Use literal dict
            if dim_line.get("type") == "tick":
                line_props["width"] = 1
            fig.add_trace(
                go.Scatter(
                    x=[dim_line["start"][0], dim_line["end"][0]],
                    y=[dim_line["start"][1], dim_line["end"][1]],
                    mode="lines",
                    line=line_props,
                    hoverinfo="none",
                )
            )

        # --- Prepare all annotations using list comprehensions ---
        all_annotations = []

        # Zone labels comprehension
        zone_annotations = [
            go.layout.Annotation(
                x=ann["x"],
                y=ann["y"],
                text=f"<b>{ann['text']}</b>",
                showarrow=False,
                font={"size": 14, "color": "DarkSlateGray"},  # Use literal dict
                ax=0,
                ay=0,
            )
            for ann in zone_annotations_data
        ]
        all_annotations.extend(zone_annotations)

        # Dimension value labels comprehension
        dimension_annotations = []
        for dim_text in dimension_texts_data:
            text_align = "center"
            xanchor = "center"
            yanchor = "middle"
            current_textangle = dim_text.get("textangle", 0)

            if current_textangle == 180:
                xanchor = "right"
                yanchor = "middle"
                text_align = "right"
            elif current_textangle in (90, -90):  # Use 'in'
                xanchor = "center"
                yanchor = "middle"
                text_align = "center"
            elif dim_text.get("type") == "length":
                text_align = "center"
                xanchor = "center"
                yanchor = "bottom"
            else:
                text_align = "left"
                xanchor = "left"
                yanchor = "middle"

            dimension_annotations.append(
                go.layout.Annotation(
                    x=dim_text["x"],
                    y=dim_text["y"],
                    text=f"<b>{dim_text['text']}</b>",
                    showarrow=False,
                    font={"size": 12, "color": "red"},  # Use literal dict
                    align=text_align,
                    xanchor=xanchor,
                    yanchor=yanchor,
                    textangle=current_textangle,
                    ax=0,
                    ay=0,
                )
            )
        all_annotations.extend(dimension_annotations)

        # Cross-section labels comprehension
        cs_label_annotations = [
            go.layout.Annotation(
                x=cs_label["x"],
                y=cs_label["y"],
                text=f"<b>{cs_label['text']}</b>",
                showarrow=False,
                font={"size": 15, "color": "black"},  # Use literal dict
                align="center",
                xanchor="center",
                yanchor="bottom",
                textangle=0,
                ax=0,
                ay=0,
            )
            for cs_label in cross_section_labels_data
        ]
        all_annotations.extend(cs_label_annotations)
        # --- End Annotation Preparation ---

        fig.update_layout(
            title="Bovenaanzicht (Top View)",
            xaxis_title="Length (m)",
            yaxis_title="Width (m)",
            showlegend=False,
            autosize=True,
            hovermode="closest",
            yaxis={  # Use literal dict
                "scaleanchor": "x",
                "scaleratio": 1,
            },
            annotations=all_annotations,
            margin={"l": 50, "r": 50, "t": 50, "b": 50},  # Use literal dict
            plot_bgcolor="white",
        )

        try:
            figure_json = fig.to_json()
            if not figure_json or figure_json == "null":
                error_fig = go.Figure()
                error_fig.update_layout(title="Error generating Top View", xaxis={"visible": False}, yaxis={"visible": False})
                error_fig.add_annotation(text="Could not generate plot. Check logs.", showarrow=False)
                return PlotlyResult(error_fig.to_json())
            return PlotlyResult(figure_json)
        except Exception as e:
            error_fig = go.Figure()
            error_fig.update_layout(title="Error generating Top View", xaxis={"visible": False}, yaxis={"visible": False})
            error_fig.add_annotation(text=f"Error: {e}. Check application logs.", showarrow=False)
            return PlotlyResult(error_fig.to_json())


    @PlotlyView("Horizontale doorsnede", duration_guess=1)
    def get_2d_horizontal_section(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002
        """
        Generates a 2D horizontal section view of the bridge using Plotly.
        
        This function creates a 2D representation of the bridge's horizontal section by:
        1. Creating a 3D model of the bridge
        2. Slicing it with a horizontal plane at the specified height
        3. Converting the resulting section into a 2D plot showing length (x) vs width (y)
        
        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            PlotlyResult: A 2D representation of the horizontal section.
        """
        fig = create_horizontal_section_view(params, params.input.dimensions.horizontal_section_loc)
        return PlotlyResult(fig.to_json())

    @PlotlyView("Langsdoorsnede", duration_guess=1)
    def get_2d_longitudinal_section(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002
        """
        Generates a 2D longitudinal section view of the bridge using Plotly.
        
        This function creates a 2D representation of the bridge's longitudinal section by:
        1. Creating a 3D model of the bridge
        2. Slicing it with a vertical plane parallel to the x-z plane
        3. Converting the resulting cross-section into a 2D plot showing length (x) vs height (z)
        
        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            PlotlyResult: A 2D representation of the longitudinal section.
        """
        fig = create_longitudinal_section(params, params.input.dimensions.longitudinal_section_loc)
        return PlotlyResult(fig.to_json())
    
    @PlotlyView("Dwarsdoorsnede", duration_guess=1)
    def get_2d_cross_section(self, params: BridgeParametrization, **kwargs) -> PlotlyResult:  # noqa: ARG002
        """
        Generates a 2D cross-section view of the bridge using Plotly.
        
        This function creates a 2D representation of the bridge's cross-section by:
        1. Creating a 3D model of the bridge
        2. Slicing it with a vertical plane parallel to the y-z plane
        3. Converting the resulting cross-section into a 2D plot showing width (y) vs height (z)
        
        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            PlotlyResult: A 2D representation of the cross-section.
        """
        fig = create_cross_section_view(params, params.input.dimensions.cross_section_loc)
        return PlotlyResult(fig.to_json())
    
    # ============================================================================================================
    # output - Rapport
    # ============================================================================================================

    @PDFView("Rapport", duration_guess=1)
    def get_output_report(self, params: BridgeParametrization, **kwargs) -> PDFResult:  # noqa: ARG002
        """
        Generates a PDF report for the bridge design.

        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            File: A PDF file containing the report.

        """
        # using File object
        file1 = File.from_path(OUTPUT_REPORT_PATH)
        with file1.open_binary() as f1:
            pdf = convert_word_to_pdf(f1)

        return PDFResult(file=pdf)
