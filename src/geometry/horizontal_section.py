"""Module for creating horizontal section views of the bridge."""

from typing import TYPE_CHECKING

import plotly.graph_objects as go
import trimesh

from src.geometry.model_creator import create_3d_model, create_cross_section

if TYPE_CHECKING:
    from app.bridge.parametrization import BridgeParametrization


def create_horizontal_section_view(params: "BridgeParametrization", section_loc: float) -> go.Figure:
    """
    Creates a 2D horizontal section view of the bridge using Plotly.
    This function creates a 2D representation of the bridge's horizontal section by:
    1. Creating a 3D model of the bridge
    2. Slicing it with a horizontal plane at the specified height
    3. Converting the resulting section into a 2D plot showing length (x) vs width (y).

    Args:
        params (dict | Munch): Input parameters for the bridge dimensions.
        section_loc (float): Location of the horizontal section along the z-axis.

    Returns:
        go.Figure: A 2D representation of the horizontal section.

    """
    # Generate the 3D model without coordinate axes
    scene = create_3d_model(params, axes=False)
    combined_mesh = trimesh.util.concatenate(scene.geometry.values())

    # Define the slicing plane for the horizontal section
    # The plane is horizontal (normal to z-axis) at the specified height
    plane_origin = [0, 0, section_loc]
    plane_normal = [0, 0, 1]

    # Create the section by slicing the 3D model
    combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal, axes=False)
    combined_scene_2d_mesh = trimesh.util.concatenate(combined_scene_2d.geometry.values())

    # Extract vertices and entities from the sliced mesh
    vertices = combined_scene_2d_mesh.vertices
    entities = combined_scene_2d_mesh.entities

    # Initialize the Plotly figure
    fig = go.Figure()

    # Collect all x and y coordinates to determine the plot range
    all_x = []
    all_y = []
    for entity in entities:
        points = entity.points
        for point in points:
            all_x.append(vertices[point][0])
            all_y.append(vertices[point][1])

    # Calculate plot ranges with padding for better visualization
    x_range = [min(all_x) - 2, max(all_x) + 2]
    y_range = [min(all_y) - 2, max(all_y) + 2]

    # Create line traces for each entity in the section
    for entity in entities:
        x = []
        y = []
        points = entity.points
        for point in points:
            x.append(vertices[point][0])
            y.append(vertices[point][1])

        # Add each line segment to the plot
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line={"color": "black"},  # Consistent black color for all lines
            )
        )

    # Prepare annotations
    all_annotations = []

    # Create lists for row_labels and l values
    row_labels = list(range(len(params.input.dimensions.bridge_segments_array)))
    l_values = []
    l_values_cumulative = []
    l_cumulative = 0
    for segment in params.input.dimensions.bridge_segments_array:
        l_values.append(segment.l)
        l_cumulative += segment.l
        l_values_cumulative.append(l_cumulative)

    zone_center_x = [cum + val / 2 for cum, val in zip(l_values_cumulative, l_values[1:])]

    # Add cross-section labels
    cross_section_labels = [
        go.layout.Annotation(
            x=cs_x,
            y=max(all_y) + 0.5,  # Position above the highest point
            text=f"<b>D-{i + 1}</b>",
            showarrow=False,
            font={"size": 15, "color": "black"},
            align="center",
            xanchor="center",
            yanchor="bottom",
            textangle=0,
            ax=0,
            ay=0,
        )
        for i, cs_x in zip(row_labels, l_values_cumulative)  # Use the extracted lists
    ]
    all_annotations.extend(cross_section_labels)

    # Add dimension annotations
    dimension_annotations = [
        # Length dimension
        go.layout.Annotation(
            x=zcx,
            y=min(all_y) - 1.0,
            text=f"<b>l = {length}m</b>",
            showarrow=False,
            font={"size": 12, "color": "red"},
            align="center",
            xanchor="center",
            yanchor="top",
            textangle=0,
            ax=0,
            ay=0,
        )
        for length, zcx in zip(l_values[1:], zone_center_x)  # Use the extracted lists
    ]
    all_annotations.extend(dimension_annotations)

    # Configure the plot layout with appropriate ranges and labels
    fig.update_layout(
        title="Horizontale doorsnede (Horizontal Section)",
        showlegend=False,
        autosize=True,
        xaxis={"range": x_range, "constrain": "domain", "title": "X-as - Lengte [m]"},
        yaxis={"range": y_range, "scaleanchor": "x", "scaleratio": 1, "title": "Y-as - Breedte [m]"},
        margin={"l": 50, "r": 50, "t": 50, "b": 50},
        annotations=all_annotations,
    )

    return fig
