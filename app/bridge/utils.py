"""Utility functions specific to the Bridge entity's UI or Plotly views."""

from typing import Any
from typing import Protocol as TypingProtocol

# Import for validate_load_zone_widths - ensure this path is correct
from src.geometry.model_creator import (
    LoadZoneGeometryData,  # BridgeSegmentDimensions is not directly used here anymore
)

# All plotting helper functions below have been moved to src/geometry/load_zone_plot.py or src/common/plot_utils.py
# get_zone_appearance_properties
# LoadZoneDataRow (protocol - canonical version in src/geometry/load_zone_geometry.py)
# calculate_zone_bottom_y_coords
# add_zone_fill_to_figure
# add_zone_boundary_lines_to_figure
# create_zone_main_label_annotation
# create_zone_width_annotations
# add_load_zone_visuals


# --- Validation --- (This section remains)
class ParamsForLoadZones(TypingProtocol):
    """Protocol defining the expected structure of params for load zone data itself."""

    load_zones_data_array: Any  # List of load zone rows - accessed directly on params due to 'name' property
    # Add other top-level param attributes if needed by validation in the future.


def validate_load_zone_widths(params: ParamsForLoadZones, geometry_data: LoadZoneGeometryData) -> list[str]:
    """
    Validates that the total width of load zones at each D-point does not exceed
    the available bridge width at that D-point.
    This version uses a pre-calculated LoadZoneGeometryData object.

    Args:
        params: The VIKTOR params object, expected to have load_zones_data_array directly.
        geometry_data: Pre-calculated geometric data for the bridge load zones.

    Returns:
        A list of warning message strings if any validation fails, otherwise an empty list.

    """
    warning_messages: list[str] = []

    # Access load_zones_data_array directly from params (as per ParamsForLoadZones protocol)
    if not hasattr(params, "load_zones_data_array") or not params.load_zones_data_array:
        # No load zones to validate.
        return warning_messages

    # Geometric data is now passed in, no need to prepare it here.
    num_defined_d_points = geometry_data.num_defined_d_points
    bridge_total_widths_at_d = geometry_data.total_widths_at_d_points
    bridge_top_structural_edge_at_d = geometry_data.y_top_structural_edge_at_d_points
    bridge_bottom_structural_edge_at_d = geometry_data.y_bridge_bottom_at_d_points

    # Use load_zones_data_array directly from params
    current_load_zones = params.load_zones_data_array
    num_load_zones = len(current_load_zones)

    if num_defined_d_points == 0:
        # This case should ideally be prevented by checks before calling validation,
        # or by prepare_load_zone_geometry_data raising an error if bridge segments are empty.
        # If prepare_load_zone_geometry_data ran, num_defined_d_points should be > 0 if segments exist.
        return ["Kan belastingzones niet valideren: geen D-punten gedefinieerd in bruggeometrie."]

    for d_idx in range(num_defined_d_points):
        current_bridge_total_width_available = bridge_total_widths_at_d[d_idx]
        current_d_point_name = f"D{d_idx + 1}"
        dx_width_field_name = f"d{d_idx + 1}_width"

        calculated_total_consumed_width_at_d = 0.0
        current_y_top_of_zone_for_calc = bridge_top_structural_edge_at_d[d_idx]

        for zone_row_idx, load_zone_row in enumerate(current_load_zones):
            # load_zone_row is an item from params.load_zones_data_array (Munch object from VIKTOR)
            # Direct attribute access (getattr) is appropriate here for fields defined in parametrization.
            if not hasattr(load_zone_row, dx_width_field_name) and zone_row_idx < num_load_zones - 1:
                # This D-field might not exist if number of bridge segments is less than MAX_LOAD_ZONE_SEGMENT_FIELDS
                # For non-last zones, treat missing dX_width as 0 for validation purposes.
                # The visibility callback in parametrization should hide these fields anyway.
                pass

            if zone_row_idx < num_load_zones - 1:
                zone_param_width_at_d = getattr(load_zone_row, dx_width_field_name, 0.0) or 0.0
                calculated_total_consumed_width_at_d += zone_param_width_at_d
                current_y_top_of_zone_for_calc -= zone_param_width_at_d
            else:  # Last load zone
                last_zone_actual_width_at_d = max(0.0, current_y_top_of_zone_for_calc - bridge_bottom_structural_edge_at_d[d_idx])
                calculated_total_consumed_width_at_d += last_zone_actual_width_at_d

        # Add a small tolerance (e.g., 1e-3 or 0.001) for floating point comparisons
        if calculated_total_consumed_width_at_d > current_bridge_total_width_available + 1e-3:
            overrun = calculated_total_consumed_width_at_d - current_bridge_total_width_available
            error_msg = (
                f"Bij {current_d_point_name}: Totale zonebreedte "
                f"({calculated_total_consumed_width_at_d:.2f}m) overschrijdt brugbreedte "
                f"({current_bridge_total_width_available:.2f}m) met {overrun:.2f}m."
            )
            warning_messages.append(error_msg)

    return warning_messages
