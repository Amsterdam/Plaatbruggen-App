"""Module for creating cross section views of the bridge."""

import plotly.graph_objects as go
import trimesh
from munch import Munch  # type: ignore[import-untyped]

from src.geometry.model_creator import create_3d_model, create_cross_section


def create_cross_section_view(params: dict | Munch, section_loc: float) -> go.Figure:
    """
    Creates a 2D cross-section view of the bridge using Plotly.
    This function creates a 2D representation of the bridge's cross-section by:
    1. Creating a 3D model of the bridge
    2. Slicing it with a vertical plane parallel to the y-z plane
    3. Converting the resulting cross-section into a 2D plot showing width (y) vs height (z).

    Args:
        params (dict | Munch): Input parameters for the bridge dimensions.
        section_loc (float): Location of the cross-section along the x-axis.

    Returns:
        go.Figure: A 2D representation of the cross-section.

    """
    # Generate the 3D model without coordinate axes
    scene = create_3d_model(params, axes=False)
    combined_mesh = trimesh.util.concatenate(scene.geometry.values())

    # Define the slicing plane for the cross-section
    # The plane is vertical (normal to x-axis) at the specified location
    plane_origin = [section_loc, 0, 0]
    plane_normal = [1, 0, 0]

    # Create the cross-section by slicing the 3D model
    combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal, axes=False)
    combined_scene_2d_mesh = trimesh.util.concatenate(combined_scene_2d.geometry.values())

    # Extract vertices and entities from the sliced mesh
    vertices = combined_scene_2d_mesh.vertices
    entities = combined_scene_2d_mesh.entities

    # Initialize the Plotly figure
    fig = go.Figure()

    # Collect all x and y coordinates to determine the plot range
    all_y = []
    all_z = []
    for entity in entities:
        points = entity.points
        for point in points:
            all_y.append(vertices[point][1])
            all_z.append(vertices[point][2])

    # Calculate plot ranges with padding for better visualization
    y_range = [min(all_y) - 2, max(all_y) + 2]
    z_range = [min(all_z) - 2, max(all_z) + 2]

    # Create line traces for each entity in the section
    for entity in entities:
        y = []
        z = []
        points = entity.points
        for point in points:
            y.append(vertices[point][1])
            z.append(vertices[point][2])

        # Add each line segment to the plot
        fig.add_trace(go.Scatter(
            x=y,
            y=z,
            mode="lines",
            line={"color": "black"}  # Consistent black color for all lines
        ))

    # Configure the plot layout with appropriate ranges and labels
    fig.update_layout(
        title="Dwarsdoorsnede (Cross Section)",
        xaxis={
            "range": y_range,
            "constrain": "domain",
            "title": "Y-as - Breedte [m]"
        },
        yaxis={
            "range": z_range,
            "scaleanchor": "x",
            "scaleratio": 2,  # Maintain aspect ratio for proper visualization
            "title": "Z-as - Hoogte [m]" # Z-as is the vertical axis shown as Y-axis in the plot
        }
    )

    return fig
