"""Controller for the Overview Bridges entity."""

# ============================================================================================================
# Imports
# ============================================================================================================

import json  # Import json module
import os  # Import os to construct path
import typing  # Import typing for ClassVar
from io import StringIO

# Add GeoPandas import (ensure it's installed in your venv)
import geopandas as gpd
import markdown

import viktor.api_v1 as api  # Import VIKTOR API
from app.common.map_utils import (  # Import shared utilities
    get_default_shapefile_path,
    get_filtered_bridges_json_path,
    get_resources_dir,
    load_and_prepare_shapefile,
    process_all_bridges_geometries,
    validate_shapefile_exists,
)
from app.constants import (  # Replace relative imports with absolute imports
    CHANGELOG_PATH,
    CSS_PATH,
    README_PATH,
)
from viktor.core import ViktorController  # Import Color, ViktorController
from viktor.errors import UserError  # Import UserError
from viktor.parametrization import Parametrization  # Import for type hint
from viktor.views import MapPoint, MapResult, MapView, WebResult, WebView  # Use MapPolygon instead of MapPolyline

# Import the parametrization from the separate file
from .parametrization import OverviewBridgesParametrization


class OverviewBridgesController(ViktorController):
    """Controller for the Overview Bridges entity."""

    label = "Overzicht Bruggen"  # Updated label
    parametrization = OverviewBridgesParametrization  # type: ignore[assignment] # Ignore potential complex assignment MyPy error
    children: typing.ClassVar[list[str]] = ["Bridge"]  # Use the alias defined in app/__init__.py
    show_children_as: typing.ClassVar[str] = "Table"  # Optional: How to display children (Table or Cards)

    # --- Map View Helper Methods ---

    @MapView("Overzicht Kaart", duration_guess=1)
    def get_map_view(self, params: Parametrization, **kwargs) -> MapResult:  # noqa: ARG002
        """Displays bridge polygons from the shapefile in the resources folder."""
        # 1. Define Paths
        try:
            shapefile_path = get_default_shapefile_path()
            allowed_bridges_path = get_filtered_bridges_json_path()

            # Using shared utility function to validate shapefile existence
            # validate_shapefile_exists now returns the path, so we use it directly
            shapefile_path = validate_shapefile_exists(shapefile_path)

            if not os.path.exists(allowed_bridges_path):
                raise UserError(f"Filter bestand niet gevonden op verwachtte locatie: {allowed_bridges_path}")  # noqa: TRY301

        except UserError as ue:
            raise UserError(str(ue))
        except Exception as e:
            raise UserError(f"Fout bij het bepalen van bestandspaden: {e}")

        # 2. Load allowed bridges list
        try:
            with open(allowed_bridges_path) as f:
                filtered_bridge_data = json.load(f)
                allowed_objectnumm = {bridge_obj.get("OBJECTNUMM") for bridge_obj in filtered_bridge_data if bridge_obj.get("OBJECTNUMM")}
        except Exception as e:
            raise UserError(f"Fout bij laden van {allowed_bridges_path}: {e}")

        # 3. Load and prepare shapefile data using the shared utility
        gdf = load_and_prepare_shapefile(shapefile_path, allowed_objectnumm)

        # 4. Process geometries if data exists using utility function
        features = []
        if gdf is not None and not gdf.empty:
            features = process_all_bridges_geometries(gdf)

        # 5. Handle case where no features were generated
        if not features:
            default_point = MapPoint(52.37, 4.89, description="Geen geldige brugpolygonen gevonden/gefilterd.")
            return MapResult([default_point])

        # 6. Return map result
        return MapResult(features)

    # --- Helper methods for regenerate_bridges_action ---

    @staticmethod
    def _get_resource_paths() -> tuple[str, str, str]:
        """Constructs and returns paths to resource files."""
        # Helper function to raise consistent error for missing filter file
        from typing import Never

        def _raise_filter_file_missing(path: str) -> Never:
            """Raises UserError with a consistent message format for missing filter file."""
            raise UserError(f"Filter bestand niet gevonden: {path}")

        try:
            resources_dir = get_resources_dir()  # Use new helper
            shapefile_path = get_default_shapefile_path()  # Use new helper
            filtered_bridges_path = get_filtered_bridges_json_path()  # Use new helper

            # Basic file existence check using shared utility
            # validate_shapefile_exists now returns the path
            try:
                shapefile_path = validate_shapefile_exists(shapefile_path)
            except UserError as ue:
                raise UserError(f"Shapefile validatie fout: {ue}")

            if not os.path.exists(filtered_bridges_path):
                _raise_filter_file_missing(filtered_bridges_path)
            else:
                return resources_dir, shapefile_path, filtered_bridges_path

        except Exception as e:
            raise UserError(f"Fout bij het bepalen van bestandspaden: {e}")

    @WebView("Readme and Changelog", duration_guess=3)
    def view_readme_changelog(self, **kwargs) -> WebResult:  # noqa: ARG002
        """
        Converts the docs files (README.md, CHANGELOG.md) to HTML and presents them in the viewer.

        :return: WebResult.
        """
        with open(README_PATH, encoding="utf-8") as f:
            html_text_readme = markdown.markdown(f.read())
        with open(CHANGELOG_PATH, encoding="utf-8") as f:
            html_text_changelog = markdown.markdown(f.read())
        with open(CSS_PATH, encoding="utf-8") as f:
            html_css = f.read()

        # Create complete HTML documents for each iframe
        readme_doc = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{html_css}</style>
        </head>
        <body>
            {html_text_readme}
        </body>
        </html>"""

        changelog_doc = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{html_css}</style>
        </head>
        <body class="changelog">
            {html_text_changelog}
        </body>
        </html>"""

        # Main HTML structure with responsive layout
        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Minimal styling for the container page only */
                html, body {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }}
                .container {{
                    display: flex;
                    height: 100vh;
                    width: 100%;
                }}
                .iframe-wrapper {{
                    flex: 1;
                    /* Use lighter border */
                    border-right: 1px solid #eaecef;
                    height: 100%;
                }}
                /* Remove border from the last wrapper */
                .iframe-wrapper:last-child {{
                    border-right: none;
                }}
                .iframe {{
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
                @media (max-width: 768px) {{
                    .container {{
                        flex-direction: column;
                    }}
                    .iframe-wrapper {{
                        height: 50%;
                        border-right: none;
                        /* Use lighter border */
                        border-bottom: 1px solid #eaecef;
                    }}
                    /* Remove border from the last wrapper on mobile */
                    .iframe-wrapper:last-child {{
                        border-bottom: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="iframe-wrapper">
                    <iframe class="iframe" srcdoc="{readme_doc.replace('"', "&quot;")}" frameborder="0"></iframe>
                </div>
                <div class="iframe-wrapper">
                    <iframe class="iframe" srcdoc="{changelog_doc.replace('"', "&quot;")}" frameborder="0"></iframe>
                </div>
            </div>
        </body>
        </html>"""

        return WebResult(html=StringIO(html_content))

    @staticmethod
    def _load_filtered_bridges(filtered_bridges_path: str) -> list[dict]:
        """Loads filtered bridge data from the JSON file."""
        try:
            with open(filtered_bridges_path) as f:
                return json.load(f)
        except Exception as e:
            raise UserError(f"Fout bij het laden van {filtered_bridges_path}: {e}")

    @staticmethod
    def _load_shapefile_and_names(shapefile_path: str) -> dict[str, str | None]:
        """Loads the shapefile and creates a mapping from OBJECTNUMM to OBJECTNAAM."""
        try:
            gdf = gpd.read_file(shapefile_path)
            objectnumm_to_name: dict[str, str | None] = {}
            for _, row in gdf.iterrows():
                numm = row.get("OBJECTNUMM")
                if numm:
                    name = row.get("OBJECTNAAM")
                    # Format ID as integer if possible - This part seems unused for map/child generation, removing F841/SIM105 issues

                    # Store None if OBJECTNAAM is missing, None, or empty/whitespace
                    objectnumm_to_name[str(numm)] = name if name and isinstance(name, str) and name.strip() else None
            # If loop completes without error, return the dictionary
            return objectnumm_to_name  # noqa: TRY300
        except Exception as e:
            raise UserError(f"Fout bij het lezen van shapefile {shapefile_path}: {e}")

    @staticmethod
    def _get_existing_child_objectnumms(entity_id: int) -> set[str]:
        """Retrieves the OBJECTNUMM of existing child entities."""
        try:
            viktor_api = api.API()
            parent_entity = viktor_api.get_entity(entity_id)
            existing_children = parent_entity.children(entity_type_names=["Bridge"])
            # Store OBJECTNUMM in child params under 'bridge_objectnumm' key
            return {
                child.last_saved_params.get("bridge_objectnumm") for child in existing_children if child.last_saved_params.get("bridge_objectnumm")
            }
        except Exception as e:
            raise UserError(f"Fout bij het ophalen van bestaande kind-entiteiten: {e}")

    def _create_missing_children(
        self,
        parent_entity_id: int,
        filtered_bridge_data: list[dict],
        objectnumm_to_name: dict[str, str | None],
        existing_objectnumms: set[str],
    ) -> None:
        """Creates child entities for bridges that do not already exist."""
        created_count = 0
        skipped_count = 0
        try:
            # Get parent entity object once
            parent_entity = api.API().get_entity(parent_entity_id)

            for bridge_data in filtered_bridge_data:
                objectnumm = bridge_data.get("OBJECTNUMM")

                if not objectnumm:
                    skipped_count += 1
                    continue

                objectnumm_str = str(objectnumm)  # Ensure comparison is consistent

                if objectnumm_str in existing_objectnumms:
                    skipped_count += 1
                    continue

                # Bridge doesn't exist, create it
                bridge_name = objectnumm_to_name.get(objectnumm_str)  # Use str for lookup

                # Format child name: "OBJECTNUMM - OBJECTNAAM" or just "OBJECTNUMM"
                child_name = f"{objectnumm_str} - {bridge_name}" if bridge_name else objectnumm_str

                # Extract additional bridge data from filtered_bridges.json
                stadsdeel = bridge_data.get("stadsdeel", "")
                straat = bridge_data.get("straat", "")
                bridge_type = bridge_data.get("type", "")
                construction_year = bridge_data.get("stichtingsjaar", "")
                usage = bridge_data.get("gebruik", "")
                arb_flag = bridge_data.get("vlag_arb", "Niet ingesteld")
                basic_test_ghpo = bridge_data.get("basale_toets_ghpo", "Niet ingesteld")

                # Additional bridge properties
                concrete_strength_class = bridge_data.get("betonsterkteklasse", "")
                steel_quality_reinforcement = bridge_data.get("staalkwaliteit_wapening", "")
                deck_layer = bridge_data.get("deklaag", "")

                # Geometric properties
                number_of_spans = bridge_data.get("aantal_velden", 1)
                static_system = bridge_data.get("statisch_systeem", "")
                crossing_angle = bridge_data.get("kruisingshoek", 90.0)
                # TODO: Multi-span bridges - these fields may contain semicolon-separated values for each span
                theoretical_length = bridge_data.get("lth", "")  # May contain: "8250; 4000; 13000; 15000; 15000;15000"
                deck_width = bridge_data.get("bbrugdek", "")  # May contain: "20816-35747" (ranges) or multiple values
                construction_height = bridge_data.get("constructiehoogte_dek", 0.0)
                slenderness = bridge_data.get("slankheid_dek", "")  # May contain: "10.44; 5.06; 16.46; 18.99; 18.99; 18.99"
                daily_length = bridge_data.get("ldag", "")

                # Structural properties
                bearing_type = bridge_data.get("opleggingen", "")
                orthotropy = bridge_data.get("orthotropie_isotropie", "")
                beams_in_slab = bridge_data.get("liggers_in_plaat", "")

                # Width distribution properties
                roadway_width = bridge_data.get("breedte_rijwegen", "")  # May contain: "15490-31236" (ranges)
                tram_width = bridge_data.get("breedte_trambaan", "")  # Tram track width
                bicycle_path_width = bridge_data.get("breedte_fietspad", "")

                # Width properties - convert from mm to m if needed
                # TODO: Multi-span bridges - sidewalk widths may contain ranges like "1418-1724"
                sidewalk_north_east_width = bridge_data.get("breedte_voetpad_noord_oost", "")  # May contain: "1418-1724"
                sidewalk_south_west_width = bridge_data.get("breedte_voetpad_zuid_west", "")  # May contain: "1418-1650"
                edge_beam_thickness = bridge_data.get("dikte_schampkant", "")
                edge_loading = bridge_data.get("randbelasting", "")

                # Convert widths from mm to m if they are numeric strings
                if sidewalk_north_east_width and str(sidewalk_north_east_width).isdigit():
                    sidewalk_north_east_width = str(float(sidewalk_north_east_width) / 1000)  # Convert mm to m
                if sidewalk_south_west_width and str(sidewalk_south_west_width).isdigit():
                    sidewalk_south_west_width = str(float(sidewalk_south_west_width) / 1000)  # Convert mm to m

                # Convert other width fields from mm to m if they are numeric strings
                if theoretical_length and str(theoretical_length).isdigit():
                    theoretical_length = str(float(theoretical_length) / 1000)  # Convert mm to m
                if deck_width and str(deck_width).isdigit():
                    deck_width = str(float(deck_width) / 1000)  # Convert mm to m
                if roadway_width and str(roadway_width).isdigit():
                    roadway_width = str(float(roadway_width) / 1000)  # Convert mm to m
                if tram_width and str(tram_width).isdigit():
                    tram_width = str(float(tram_width) / 1000)  # Convert mm to m
                if bicycle_path_width and str(bicycle_path_width).isdigit():
                    bicycle_path_width = str(float(bicycle_path_width) / 1000)  # Convert mm to m

                # Assessment properties
                contractor_iha = bridge_data.get("opdrachtnemer_iha", "")

                # Reinforcement data
                support_reinforcement_diameter = bridge_data.get("steunpuntswapening_langsrichting_diameter", "")
                support_reinforcement_spacing = bridge_data.get("steunpuntswapening_langsrichting_hoh_afstand", "")
                support_reinforcement_layer = bridge_data.get("steunpuntswapening_laag", "")
                field_reinforcement_diameter = bridge_data.get("veldwapening_langsrichting_diameter", "")
                field_reinforcement_spacing = bridge_data.get("veldwapening_langsrichting_hoh_afstand", "")
                field_reinforcement_layer = bridge_data.get("veldwapening_langsrichting_laag", "")
                field_reinforcement_transverse_diameter = bridge_data.get("veldwapening_dwarsrichting_diameter", "")
                field_reinforcement_transverse_spacing = bridge_data.get("veldwapening_dwarsrichting_hoh_afstand", "")
                field_reinforcement_transverse_layer = bridge_data.get("veldwapening_dwarsrichting_laag", "")
                concrete_cover = bridge_data.get("dekking_buitenkant_wapening", "")

                # Prepare parameters for the child entity, now nested under 'info'
                child_params = {
                    "info": {
                        "bridge_objectnumm": objectnumm_str,  # Store as string
                        "bridge_name": bridge_name,  # Store name or None
                        "stadsdeel": stadsdeel if stadsdeel else "",
                        "straat": straat if straat else "",
                        "bridge_type": bridge_type if bridge_type else "",
                        "construction_year": str(construction_year) if construction_year else "",
                        "usage": usage if usage else "",
                        "arb_flag": arb_flag
                        if arb_flag and arb_flag in ["puur groen", "groen/oranje", "oranje/groen", "puur oranje", "oranje/rood", "puur rood"]
                        else "Niet ingesteld",
                        "basic_test_ghpo": basic_test_ghpo
                        if basic_test_ghpo and basic_test_ghpo in ["groen", "oranje", "rood", "nvt", "Wel"]
                        else "Niet ingesteld",
                        "concrete_strength_class": concrete_strength_class if concrete_strength_class else "",
                        "steel_quality_reinforcement": steel_quality_reinforcement if steel_quality_reinforcement else "",
                        "deck_layer": deck_layer if deck_layer else "",
                        "number_of_spans": number_of_spans if isinstance(number_of_spans, int) else 1,
                        "static_system": static_system if static_system else "",
                        "crossing_angle": crossing_angle if isinstance(crossing_angle, (int, float)) else 90.0,
                        "theoretical_length": theoretical_length if theoretical_length else "",
                        "deck_width": deck_width if deck_width else "",
                        "construction_height": construction_height if isinstance(construction_height, (int, float)) else 0.0,
                        "slenderness": slenderness if slenderness else "",
                        "daily_length": daily_length if daily_length else "",
                        "bearing_type": bearing_type if bearing_type else "",
                        "orthotropy": orthotropy if orthotropy else "",
                        "beams_in_slab": "Ja"
                        if beams_in_slab and str(beams_in_slab).lower() in ["ja", "yes", "true"]
                        else ("Nee" if beams_in_slab and str(beams_in_slab).lower() in ["nee", "no", "false"] else "Onbekend"),
                        "roadway_width": roadway_width if roadway_width else "",
                        "tram_width": tram_width if tram_width else "",
                        "bicycle_path_width": bicycle_path_width if bicycle_path_width else "",
                        "sidewalk_north_east_width": sidewalk_north_east_width if sidewalk_north_east_width else "",
                        "sidewalk_south_west_width": sidewalk_south_west_width if sidewalk_south_west_width else "",
                        "edge_beam_thickness": edge_beam_thickness if edge_beam_thickness else "",
                        "edge_loading": "Ja"
                        if edge_loading and str(edge_loading).lower() in ["ja", "true", "1"]
                        else ("Nee" if edge_loading and str(edge_loading).lower() in ["nee", "false", "0"] else "Onbekend"),
                        "contractor_iha": contractor_iha if contractor_iha else "",
                        "support_reinforcement_diameter": support_reinforcement_diameter if support_reinforcement_diameter else "",
                        "support_reinforcement_spacing": support_reinforcement_spacing if support_reinforcement_spacing else "",
                        "support_reinforcement_layer": support_reinforcement_layer if support_reinforcement_layer else "",
                        "field_reinforcement_diameter": field_reinforcement_diameter if field_reinforcement_diameter else "",
                        "field_reinforcement_spacing": field_reinforcement_spacing if field_reinforcement_spacing else "",
                        "field_reinforcement_layer": field_reinforcement_layer if field_reinforcement_layer else "",
                        "field_reinforcement_transverse_diameter": field_reinforcement_transverse_diameter
                        if field_reinforcement_transverse_diameter
                        else "",
                        "field_reinforcement_transverse_spacing": field_reinforcement_transverse_spacing
                        if field_reinforcement_transverse_spacing
                        else "",
                        "field_reinforcement_transverse_layer": field_reinforcement_transverse_layer if field_reinforcement_transverse_layer else "",
                        "concrete_cover": concrete_cover if concrete_cover else "",
                    }
                }

                # Call create_child on the parent entity object
                parent_entity.create_child(entity_type_name="Bridge", name=child_name, params=child_params)
                created_count += 1
                # Add to set to prevent potential duplicates within this run
                existing_objectnumms.add(objectnumm_str)

        except Exception as e:
            raise UserError(f"Fout tijdens het aanmaken van kind-entiteiten: {e}")

    # --- Main Action Method ---

    def regenerate_bridges_action(self, entity_id: int, **kwargs) -> None:  # noqa: ARG002
        """Loads bridges from filtered_bridges.json and creates child entities if they don't exist."""
        # even if it is unused within the method body.
        # 1. Get paths
        _resources_dir, shapefile_path, filtered_bridges_path = self._get_resource_paths()

        # 2. Load data
        filtered_bridge_data = self._load_filtered_bridges(filtered_bridges_path)
        objectnumm_to_name = self._load_shapefile_and_names(shapefile_path)

        # 3. Get existing children
        existing_objectnumms = self._get_existing_child_objectnumms(entity_id)

        # 4. Create missing children
        self._create_missing_children(
            parent_entity_id=entity_id,
            filtered_bridge_data=filtered_bridge_data,
            objectnumm_to_name=objectnumm_to_name,
            existing_objectnumms=existing_objectnumms,
        )
        # No explicit return needed (implicitly returns None)
