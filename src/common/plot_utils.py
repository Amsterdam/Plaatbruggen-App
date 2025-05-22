"""Common utility functions for Plotly plots within the src layer."""

from typing import Any

import plotly.graph_objects as go


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


def create_structural_polygons_traces(zone_polygons_data: list[dict[str, Any]]) -> list[go.Scatter]:
    """
    Creates Scatter traces for structural zone polygons.

    Args:
        zone_polygons_data: A list of dictionaries, where each dictionary represents a polygon
                             and contains 'vertices' (list of [x,y] points) and optionally 'color'.

    Returns:
        A list of go.Scatter traces for the polygons.

    """
    traces = []
    for poly_data in zone_polygons_data:
        vertices = poly_data.get("vertices", [])
        if not vertices or len(vertices) < 3:  # Need at least 3 vertices
            continue

        x_coords_poly = [v[0] for v in vertices] + [vertices[0][0]]  # Close polygon
        y_coords_poly = [v[1] for v in vertices] + [vertices[0][1]]  # Close polygon
        color = poly_data.get("color", "rgba(220,220,220,0.4)")  # Default color

        traces.append(
            go.Scatter(
                x=x_coords_poly,
                y=y_coords_poly,
                mode="lines",
                fill="toself",
                fillcolor=color,
                line={"width": 0.5, "color": "rgba(100, 100, 100, 0.5)"},  # Default thin border
                hoverinfo="skip",
                showlegend=False,
            )
        )
    return traces


def create_bridge_outline_traces(bridge_lines_data: list[dict[str, Any]]) -> list[go.Scatter]:
    """
    Creates Scatter traces for the bridge outline segments.

    Args:
        bridge_lines_data: A list of dictionaries, each representing a line segment
                           and contains 'start' ([x,y] point) and 'end' ([x,y] point),
                           and optionally 'color' and 'width'.

    Returns:
        A list of go.Scatter traces for the bridge outline.

    """
    traces = []
    for line_segment in bridge_lines_data:
        start_point = line_segment.get("start")
        end_point = line_segment.get("end")

        if not start_point or not end_point:
            continue

        # Use defaults consistent with original app/bridge/utils.py if not provided
        color = line_segment.get("color", "grey")
        width = line_segment.get("width", 1)

        traces.append(
            go.Scatter(
                x=[start_point[0], end_point[0]],
                y=[start_point[1], end_point[1]],
                mode="lines",
                line={"color": color, "width": width},
                hoverinfo="none",
                showlegend=False,
            )
        )
    return traces
