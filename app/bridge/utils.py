"""Utility functions specific to the Bridge entity's UI or Plotly views."""

from typing import Any, Protocol

import plotly.graph_objects as go
from plotly.colors import qualitative as qual_colors

# --- Helper functions for add_load_zone_visuals (and d_point_annotations) ---


def create_text_annotations_from_data(  # noqa: PLR0913
    label_data: list[dict[str, Any]],
    font_size: int = 12,
    font_color: str = "black",
    xanchor: str = "center",
    yanchor: str = "bottom",
    showarrow: bool = False,
    text_prefix: str = "<b>",
    text_suffix: str = "</b>",
    **kwargs,  # To pass any other go.layout.Annotation properties
) -> list[go.layout.Annotation]:
    """
    Creates a list of Plotly text annotations from a list of data dictionaries.

    Args:
        label_data: List of dictionaries, each with 'text', 'x', 'y' keys.
        font_size: Font size for the annotation text.
        font_color: Color of the annotation text.
        xanchor: Horizontal anchor for the text.
        yanchor: Vertical anchor for the text.
        showarrow: Whether to show an arrow pointing to the annotation.
        text_prefix: Prefix for the text (e.g., for bold tags).
        text_suffix: Suffix for the text (e.g., for bold tags).
        **kwargs: Additional properties to pass to go.layout.Annotation.

    Returns:
        A list of go.layout.Annotation objects.

    """
    return [
        go.layout.Annotation(
            x=data_item["x"],
            y=data_item["y"],
            text=f"{text_prefix}{data_item['text']}{text_suffix}",
            font={"size": font_size, "color": font_color},
            xanchor=xanchor,
            yanchor=yanchor,
            showarrow=showarrow,
            **kwargs,
        )
        for data_item in label_data
    ]


def get_zone_appearance_properties(
    zone_type_text: str,
    zone_idx: int,
    zone_appearance_map: dict[str, dict[str, Any]],
    default_plotly_colors: list[str],
) -> dict[str, Any]:
    """Determines visual properties for a load zone based on its type and index."""
    appearance = zone_appearance_map.get(zone_type_text)
    if appearance:
        return {
            "line_color": appearance["line_color"],
            "fill_color": appearance["fill_color"],
            "pattern_shape": appearance.get("pattern_shape", ""),
            "pattern_fgcolor": appearance.get("pattern_fgcolor", appearance["line_color"]),
            "pattern_solidity": appearance.get("pattern_solidity", 0.4),
        }

    # Fallback for types not in the map
    line_color = default_plotly_colors[zone_idx % len(default_plotly_colors)]
    fill_color = "rgba(200,200,200,0.1)"  # Default light gray
    try:
        if line_color.startswith("rgb("):
            base_rgb = line_color[4:-1]
            fill_color = f"rgba({base_rgb},0.1)"
    except Exception:
        pass  # Stick to default light gray on any error

    return {
        "line_color": line_color,
        "fill_color": fill_color,
        "pattern_shape": ".",
        "pattern_fgcolor": line_color,
        "pattern_solidity": 0.3,
    }


# Define a protocol for the expected structure of zone_param_data
class LoadZoneDataRow(Protocol):
    """Protocol defining the expected structure for a row of load zone parameter data."""

    zone_type: str
    # Add dX_width fields that are accessed via getattr
    # While getattr is used, having them in the protocol can aid understanding
    # and potentially catch typos if direct access were ever used.
    d1_width: float
    d2_width: float
    d3_width: float
    d4_width: float
    d5_width: float
    d6_width: float
    d7_width: float
    d8_width: float
    d9_width: float
    d10_width: float
    d11_width: float
    d12_width: float
    d13_width: float
    d14_width: float
    d15_width: float


def calculate_zone_bottom_y_coords(  # noqa: PLR0913
    zone_idx: int,
    num_load_zones: int,
    num_defined_d_points: int,
    y_coords_top_current_zone: list[float],
    y_bridge_bottom_at_d_points: list[float],
    zone_param_data: LoadZoneDataRow,  # Use the protocol
) -> list[float]:
    """Calculates the Y-coordinates for the bottom boundary of the current load zone."""
    if zone_idx == num_load_zones - 1:
        return list(y_bridge_bottom_at_d_points)

    y_coords_bottom = []
    for d_idx_loop in range(num_defined_d_points):
        d_field_name = f"d{d_idx_loop + 1}_width"
        zone_width_at_this_d_point = getattr(zone_param_data, d_field_name, 0.0)
        y_bottom_val = y_coords_top_current_zone[d_idx_loop] - zone_width_at_this_d_point
        y_coords_bottom.append(y_bottom_val)
    return y_coords_bottom


def add_zone_fill_to_figure(
    fig: go.Figure,
    x_coords: list[float],
    y_coords_top: list[float],
    y_coords_bottom: list[float],
    appearance_props: dict[str, Any],
) -> None:
    """Adds a filled scatter trace representing a load zone to the figure."""
    if not (x_coords and y_coords_top and y_coords_bottom):
        return

    fill_x_coords = list(x_coords) + list(x_coords)[::-1]
    fill_y_coords = list(y_coords_top) + list(y_coords_bottom)[::-1]

    fig.add_trace(
        go.Scatter(
            x=fill_x_coords,
            y=fill_y_coords,
            mode="none",
            fill="toself",
            fillcolor=appearance_props["fill_color"],
            fillpattern_shape=appearance_props["pattern_shape"],
            fillpattern_fgcolor=appearance_props["pattern_fgcolor"],
            fillpattern_solidity=appearance_props["pattern_solidity"],
            hoverinfo="skip",
            showlegend=False,
        )
    )


def add_zone_boundary_lines_to_figure(  # noqa: PLR0913
    fig: go.Figure,
    zone_idx: int,
    num_load_zones: int,
    x_coords: list[float],
    y_coords_top: list[float],
    y_coords_bottom: list[float],
    line_color: str,
    sbs_line_thickness: float,
    sbs_offset: float,
    absolute_edge_thickness: float,
) -> None:
    """Adds top and bottom boundary lines for a load zone to the figure."""
    # TOP boundary
    if zone_idx == 0:  # Absolute top edge of the first zone
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords_top,
                mode="lines",
                line={"color": line_color, "width": absolute_edge_thickness},
                showlegend=False,
            )
        )
    else:  # Shared (side-by-side) boundary - top of current zone
        y_visual_top_boundary_part = [y - sbs_offset for y in y_coords_top]
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_visual_top_boundary_part,
                mode="lines",
                line={"color": line_color, "width": sbs_line_thickness},
                showlegend=False,
            )
        )

    # BOTTOM boundary
    if zone_idx == num_load_zones - 1:  # Absolute bottom edge of the last zone
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords_bottom,
                mode="lines",
                line={"color": line_color, "width": absolute_edge_thickness},
                showlegend=False,
            )
        )
    else:  # Shared (side-by-side) boundary - bottom of current zone
        y_visual_bottom_boundary_part = [y + sbs_offset for y in y_coords_bottom]
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_visual_bottom_boundary_part,
                mode="lines",
                line={"color": line_color, "width": sbs_line_thickness},
                showlegend=False,
            )
        )


def create_zone_main_label_annotation(
    zone_idx: int,
    zone_type_text: str,
    x_coords_d_points: list[float],
    y_coords_top_current_zone: list[float],
    y_coords_bottom_current_zone: list[float],
) -> go.layout.Annotation:
    """Creates the main label annotation for a load zone (e.g., 'bz1: Type')."""
    y_top_for_main_annotation_at_end = y_coords_top_current_zone[-1]
    y_bottom_for_main_annotation_at_end = y_coords_bottom_current_zone[-1]
    main_annotation_y_pos = (y_top_for_main_annotation_at_end + y_bottom_for_main_annotation_at_end) / 2
    main_annotation_x_pos = x_coords_d_points[-1] + 2.0  # Offset from end

    return go.layout.Annotation(
        x=main_annotation_x_pos,
        y=main_annotation_y_pos,
        text=f"<b>bz{zone_idx + 1}</b>: <i>{zone_type_text}</i>",
        showarrow=False,
        font={"size": 10, "color": "black"},
        xanchor="left",
        yanchor="middle",
    )


def create_zone_width_annotations(
    zone_param_data: LoadZoneDataRow,  # Use the protocol
    x_coords_d_points: list[float],
    y_coords_top_current_zone: list[float],
    y_coords_bottom_current_zone: list[float],
    num_defined_d_points: int,
) -> list[go.layout.Annotation]:
    """Creates width annotations for each D-section within a load zone."""
    width_annotations = []
    for d_idx in range(num_defined_d_points):
        d_field_name = f"d{d_idx + 1}_width"
        zone_width_at_d_section = getattr(zone_param_data, d_field_name, 0.0)

        if zone_width_at_d_section > 0.01:  # Only annotate if width is significant
            y_top_at_d = y_coords_top_current_zone[d_idx]
            y_bottom_at_d = y_coords_bottom_current_zone[d_idx]

            if y_top_at_d > y_bottom_at_d:
                width_annotation_y_pos = (y_top_at_d + y_bottom_at_d) / 2.0
                width_annotation_x_pos = x_coords_d_points[d_idx]

                width_annotations.append(
                    go.layout.Annotation(
                        x=width_annotation_x_pos,
                        y=width_annotation_y_pos,
                        text=f"{zone_width_at_d_section:.2f}m",
                        showarrow=False,
                        font={"size": 8, "color": "black"},
                        xanchor="center",
                        yanchor="middle",
                        bgcolor="rgba(255,255,255,0.6)",
                        borderpad=1,
                    )
                )
    return width_annotations


def add_load_zone_visuals(
    fig: go.Figure,
    load_zones_data: list,
    geometry_data: dict[str, Any],
) -> list[go.layout.Annotation]:
    """Adds load zone lines, custom fills, and type annotations using helper functions."""
    zone_annotations: list[go.layout.Annotation] = []

    x_coords_d_points = geometry_data.get("x_coords", [])
    y_bridge_bottom_at_d_points = geometry_data.get("y_bottom_edge", [])
    num_defined_d_points = geometry_data.get("num_points", 0)

    if not load_zones_data or num_defined_d_points == 0:
        return zone_annotations

    # Define line thicknesses and offset for side-by-side effect
    sbs_line_thickness = 3
    sbs_offset = sbs_line_thickness / 60.0
    absolute_edge_thickness = sbs_line_thickness

    # Define custom appearance map for load zone types
    zone_appearance_map: dict[str, dict[str, Any]] = {
        "Voetgangers": {
            "line_color": "silver",
            "pattern_shape": "+",
            "pattern_fgcolor": "silver",
            "fill_color": "rgba(192,192,192,0.2)",
            "pattern_solidity": 0.5,
        },
        "Fietsers": {
            "line_color": "crimson",
            "pattern_shape": "",
            "fill_color": "rgba(220,20,60,0.3)",
        },
        "Auto": {
            "line_color": "darkslategrey",
            "pattern_shape": "",
            "fill_color": "rgba(47,79,79,0.15)",
        },
    }
    default_plotly_colors = qual_colors.Plotly

    y_coords_mathematical_top_of_current_zone = list(geometry_data.get("y_top_edge", []))
    num_load_zones = len(load_zones_data)

    for zone_idx, zone_param_data in enumerate(load_zones_data):
        zone_type_text = getattr(zone_param_data, "zone_type", "N/A")

        appearance_props = get_zone_appearance_properties(zone_type_text, zone_idx, zone_appearance_map, default_plotly_colors)

        y_coords_mathematical_bottom_of_current_zone = calculate_zone_bottom_y_coords(
            zone_idx,
            num_load_zones,
            num_defined_d_points,
            y_coords_mathematical_top_of_current_zone,
            y_bridge_bottom_at_d_points,
            zone_param_data,
        )

        add_zone_fill_to_figure(
            fig,
            x_coords_d_points,
            y_coords_mathematical_top_of_current_zone,
            y_coords_mathematical_bottom_of_current_zone,
            appearance_props,
        )

        add_zone_boundary_lines_to_figure(
            fig,
            zone_idx,
            num_load_zones,
            x_coords_d_points,
            y_coords_mathematical_top_of_current_zone,
            y_coords_mathematical_bottom_of_current_zone,
            appearance_props["line_color"],
            sbs_line_thickness,
            sbs_offset,
            absolute_edge_thickness,
        )

        main_label_annotation = create_zone_main_label_annotation(
            zone_idx,
            zone_type_text,
            x_coords_d_points,
            y_coords_mathematical_top_of_current_zone,
            y_coords_mathematical_bottom_of_current_zone,
        )
        zone_annotations.append(main_label_annotation)

        width_annotations = create_zone_width_annotations(
            zone_param_data,
            x_coords_d_points,
            y_coords_mathematical_top_of_current_zone,
            y_coords_mathematical_bottom_of_current_zone,
            num_defined_d_points,
        )
        zone_annotations.extend(width_annotations)

        y_coords_mathematical_top_of_current_zone = list(y_coords_mathematical_bottom_of_current_zone)

    return zone_annotations
