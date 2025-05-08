"""
Provides functions for creating 3D geometric models, including boxes, axes,
and cross-sections, using the `trimesh` library. It also includes functionality for
generating a 3D representation of a bridge deck based on input parameters.
"""

import numpy as np
import trimesh
from munch import Munch  # type: ignore[import-untyped]


# Function to create a box by specifying its vertices and faces
def create_box(vertices: np.ndarray, color: list) -> trimesh.Trimesh:
    """
    Create a box mesh from specified vertices.

    Args:
        vertices (np.ndarray): Array of 8 vertices (corners of the box) as [x, y, z].
        color (list): RGBA color for the box (single color).

    Returns:
        trimesh.Trimesh: A trimesh object representing the box.

    """
    # Define faces using vertex indices (triangles)
    faces = np.array(
        [
            # Bottom face
            [0, 1, 2],
            [0, 2, 3],
            # Top face
            [4, 5, 6],
            [4, 6, 7],
            # Front face
            [0, 1, 5],
            [0, 5, 4],
            # Back face
            [3, 2, 6],
            [3, 6, 7],
            # Left face
            [0, 3, 7],
            [0, 7, 4],
            # Right face
            [1, 2, 6],
            [1, 6, 5],
        ]
    )
    # Create the mesh
    box_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Assign the same color to all faces
    box_mesh.visual.face_colors = np.array([color] * len(box_mesh.faces))
    return box_mesh


# Function to create the X, Y, and Z axes
def create_axes(length: float = 5.0, radius: float = 0.05) -> trimesh.Scene:
    """
    Create X, Y, Z axes as cylinders or lines at the origin.

    Args:
        length (float): Length of the axes.
        radius (float): Radius of the cylinder representing each axis.

    Returns:
        trimesh.Scene: A scene containing the axes as colored cylinders.

    """
    # Create cylinder meshes for each axis
    x_axis = trimesh.creation.cylinder(radius=radius, height=length, sections=20)
    y_axis = trimesh.creation.cylinder(radius=radius, height=length, sections=20)
    z_axis = trimesh.creation.cylinder(radius=radius, height=length, sections=20)

    # Rotate cylinders to align with their respective axes
    x_axis.vertices = (
        trimesh.transformations.rotation_matrix(angle=np.pi / 2, direction=[0, 1, 0], point=[0, 0, 0])
        .dot(np.hstack((x_axis.vertices, np.ones((x_axis.vertices.shape[0], 1)))).T)
        .T[:, :3]
    )
    y_axis.vertices = (
        trimesh.transformations.rotation_matrix(angle=np.pi / 2, direction=[1, 0, 0], point=[0, 0, 0])
        .dot(np.hstack((y_axis.vertices, np.ones((y_axis.vertices.shape[0], 1)))).T)
        .T[:, :3]
    )

    # Translate cylinders to align with the origin and direction of each axis
    x_axis.apply_translation([length / 2, 0, 0])  # Translate along X-axis
    y_axis.apply_translation([0, length / 2, 0])  # Translate along Y-axis
    z_axis.apply_translation([0, 0, length / 2])  # Translate along Z-axis

    # Apply colors to the axes
    x_axis.visual.face_colors = [255, 0, 0, 255]  # Red for X-axis
    y_axis.visual.face_colors = [0, 255, 0, 255]  # Green for Y-axis
    z_axis.visual.face_colors = [0, 0, 255, 255]  # Blue for Z-axis

    # Combine axes into a single scene
    return trimesh.Scene([x_axis, y_axis, z_axis])


# Function to create a black dot at the origin
def create_black_dot(radius: float = 0.2) -> trimesh.Trimesh:
    """
    Create a black sphere (dot) at the origin.

    Args:
        radius (float): Radius of the sphere.

    Returns:
        trimesh.Trimesh: A sphere mesh representing the black dot.

    """
    # Create a sphere mesh and assign black color
    dot = trimesh.creation.icosphere(radius=radius)
    dot.visual.face_colors = [0, 0, 0, 255]  # Black color
    return dot


def create_cross_section(mesh: trimesh.Trimesh, plane_origin: list | np.ndarray, plane_normal: list | np.ndarray) -> trimesh.Scene:
    """
    Create a cross-section of a 3D mesh by slicing it with a plane.

    Args:
        mesh (trimesh.Trimesh): The 3D mesh to slice.
        plane_origin (list or np.ndarray): A point on the slicing plane [x, y, z].
        plane_normal (list or np.ndarray): The normal vector of the slicing plane [nx, ny, nz].

    Returns:
        trimesh.path.Path3D: A 3D path representing the cross-section.

    """
    # Ensure the plane origin and normal are numpy arrays
    plane_origin = np.array(plane_origin)
    plane_normal = np.array(plane_normal)

    # Slice the mesh with the specified plane
    cross_section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)

    combined_scene_2d = trimesh.Scene(cross_section)

    # Add the X, Y, Z axes to the scene
    axes_scene = create_axes()
    combined_scene_2d.add_geometry(axes_scene)

    # Add the black dot at the origin to the scene
    black_dot = create_black_dot(radius=0.1)
    combined_scene_2d.add_geometry(black_dot)

    return combined_scene_2d


def create_3d_model(params: (dict | Munch)) -> trimesh.Scene:
    """
    Generates a 3D representation of a bridge deck based on input parameters.

    Args:
        params (dict | Munch): Input parameters containing bridge dimensions and properties.
            - params.input.dimensions.array: A list of dictionaries, where each dictionary
              defines the dimensions and properties of a sub-zone. Each dictionary should
              include keys such as 'l', 'bz1', 'bz2', 'bz3', 'dz', and 'dze'.

    Returns:
        trimesh.Scene: A 3D scene containing the bridge deck model, including sub-zone boxes,
        axes, and a black dot at the origin.

    """
    # Determine the number of sub-zones based on input dimensions
    sub_zones = len(params.input.dimensions.array)

    # Generate a dynamic color list for the sub-zones
    clist = list(range(0, 255, int(float(255 / sub_zones))))
    clist.insert(0, 0)

    # Initialize an empty scene for the 3D model
    combined_scene = trimesh.Scene()

    # Iterate through each sub-zone to create 3D boxes
    for i in range(1, sub_zones):
        # Calculate cumulative length for the current sub-zone
        num_dicts_to_sum = i
        l_sum = sum(item["l"] for item in params.input.dimensions.array[:num_dicts_to_sum])

        # Define dimensions for the previous and current zones
        ## D n-1
        d0l = l_sum
        # Zone 1
        z1d0l = params.input.dimensions.array[i - 1].bz1 + params.input.dimensions.array[i - 1].bz2 / 2
        z1d0r = params.input.dimensions.array[i - 1].bz2 / 2
        z1d0t = 0
        z1d0b = -params.input.dimensions.array[i - 1].dz
        # Zone 2
        z2d0l = params.input.dimensions.array[i - 1].bz2 / 2
        z2d0r = -params.input.dimensions.array[i - 1].bz2 / 2
        z2d0t = params.input.dimensions.array[i - 1].dze
        z2d0b = -params.input.dimensions.array[i - 1].dz
        # Zone 3
        z3d0l = -params.input.dimensions.array[i - 1].bz2 / 2
        z3d0r = -params.input.dimensions.array[i - 1].bz3 - params.input.dimensions.array[i - 1].bz2 / 2
        z3d0t = 0
        z3d0b = -params.input.dimensions.array[i - 1].dz

        ## D
        # Zone 1
        d1l = params.input.dimensions.array[i].l + l_sum
        z1d1l = params.input.dimensions.array[i].bz1 + params.input.dimensions.array[i].bz2 / 2
        z1d1r = params.input.dimensions.array[i].bz2 / 2
        z1d1t = 0
        z1d1b = -params.input.dimensions.array[i].dz
        # Zone 2
        z2d1l = params.input.dimensions.array[i].bz2 / 2
        z2d1r = -params.input.dimensions.array[i].bz2 / 2
        z2d1t = params.input.dimensions.array[i].dze
        z2d1b = -params.input.dimensions.array[i].dz
        # Zone 3
        z3d1l = -params.input.dimensions.array[i].bz2 / 2
        z3d1r = -params.input.dimensions.array[i].bz3 - params.input.dimensions.array[i].bz2 / 2
        z3d1t = 0
        z3d1b = -params.input.dimensions.array[i].dz

        # Specify the vertices for each box, shifted along the Y-axis
        boxes_vertices = [
            # Box 1 (at origin in Y-axis)
            np.array(
                [
                    [d0l, z1d0r, z1d0b],  # Vertex 0: Bottom-front-left -- D-1
                    [d1l, z1d1r, z1d1b],  # Vertex 1: Bottom-front-right
                    [d1l, z1d1l, z1d1b],  # Vertex 2: Bottom-back-right
                    [d0l, z1d0l, z1d0b],  # Vertex 3: Bottom-back-left -- D-1
                    [d0l, z1d0r, z1d0t],  # Vertex 4: Top-front-left -- D-1
                    [d1l, z1d1r, z1d1t],  # Vertex 5: Top-front-right
                    [d1l, z1d1l, z1d1t],  # Vertex 6: Top-back-right
                    [d0l, z1d0l, z1d0t],  # Vertex 7: Top-back-left -- D-1
                ]
            ),
            # Box 2 (shifted along Y-axis by 3 units)
            np.array(
                [
                    [d0l, z2d0r, z2d0b],  # Vertex 0: Bottom-front-left -- D-1
                    [d1l, z2d1r, z2d1b],  # Vertex 1: Bottom-front-right
                    [d1l, z2d1l, z2d1b],  # Vertex 2: Bottom-back-right
                    [d0l, z2d0l, z2d0b],  # Vertex 3: Bottom-back-left -- D-1
                    [d0l, z2d0r, z2d0t],  # Vertex 4: Top-front-left -- D-1
                    [d1l, z2d1r, z2d1t],  # Vertex 5: Top-front-right
                    [d1l, z2d1l, z2d1t],  # Vertex 6: Top-back-right
                    [d0l, z2d0l, z2d0t],  # Vertex 7: Top-back-left -- D-1
                ]
            ),
            # Box 3 (shifted along Y-axis by 6 units)
            np.array(
                [
                    [d0l, z3d0r, z3d0b],  # Vertex 0: Bottom-front-left -- D-1
                    [d1l, z3d1r, z3d1b],  # Vertex 1: Bottom-front-right
                    [d1l, z3d1l, z3d1b],  # Vertex 2: Bottom-back-right
                    [d0l, z3d0l, z3d0b],  # Vertex 3: Bottom-back-left -- D-1
                    [d0l, z3d0r, z3d0t],  # Vertex 4: Top-front-left -- D-1
                    [d1l, z3d1r, z3d1t],  # Vertex 5: Top-front-right
                    [d1l, z3d1l, z3d1t],  # Vertex 6: Top-back-right
                    [d0l, z3d0l, z3d0t],  # Vertex 7: Top-back-left -- D-1
                ]
            ),
        ]

        # Define colors for each box in RGBA format
        box_colors = [
            [255, clist[i], clist[i], 255],  # Box 1: Red
            [clist[i], clist[i], 255, 255],  # Box 2: Blue
            [clist[i], 255, clist[i], 255],  # Box 3: Green
        ]

        # Create individual box meshes with assigned colors
        box_meshes = []
        for vertices, color in zip(boxes_vertices, box_colors):
            box_mesh = create_box(vertices, color)  # Use updated create_box
            box_meshes.append(box_mesh)

        # Combine all box meshes into a single mesh
        combined_vertices = []
        combined_faces = []
        vertex_offset = 0

        for mesh in box_meshes:
            # Append vertices
            combined_vertices.append(mesh.vertices)
            # Append faces, adjusting indices by the current vertex offset
            combined_faces.append(mesh.faces + vertex_offset)
            # Update vertex offset for the next mesh
            vertex_offset += len(mesh.vertices)

        # Stack all vertices and faces into single arrays
        final_vertices = np.vstack(combined_vertices)
        final_faces = np.vstack(combined_faces)

        # Create the final combined mesh
        combined_mesh = trimesh.Trimesh(vertices=final_vertices, faces=final_faces)

        combined_scene.add_geometry(combined_mesh)

    # Add the X, Y, Z axes to the scene
    axes_scene = create_axes()
    combined_scene.add_geometry(axes_scene)

    # Add the black dot at the origin to the scene
    black_dot = create_black_dot(radius=0.1)
    combined_scene.add_geometry(black_dot)

    return combined_scene
