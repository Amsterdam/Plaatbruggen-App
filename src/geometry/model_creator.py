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
            - params.bridge_segments_array: A list of dictionaries, where each dictionary
              defines the dimensions and properties of a sub-zone. Each dictionary should
              include keys such as 'l', 'bz1', 'bz2', 'bz3', 'dz', and 'dze'.

    Returns:
        trimesh.Scene: A 3D scene containing the bridge deck model, including sub-zone boxes,
        axes, and a black dot at the origin.

    """
    # Determine the number of sub-zones based on input dimensions
    dynamic_arrays = len(params.bridge_segments_array)

    # Generate a dynamic color list for the sub-zones
    clist = list(range(0, 255, int(float(255 / dynamic_arrays))))
    clist.insert(0, 0)

    # Initialize an empty scene for the 3D model
    combined_scene = trimesh.Scene()

    # Iterate through each sub-zone to create 3D boxes
    for dynamic_array in range(1, dynamic_arrays):
        # Calculate cumulative length for the current sub-zone
        num_dicts_to_sum = dynamic_array
        l_sum = sum(item["l"] for item in params.bridge_segments_array[:num_dicts_to_sum])

        # Define dimensions for the previous and current zones
        ## D n-1
        d0l = l_sum
        # Zone 1
        z1d0l = params.bridge_segments_array[dynamic_array - 1].bz1 + params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z1d0r = params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z1d0t = 0
        z1d0b = -params.bridge_segments_array[dynamic_array - 1].dz
        # Zone 2
        z2d0l = params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z2d0r = -params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z2d0t = params.bridge_segments_array[dynamic_array - 1].dz_2 - params.bridge_segments_array[dynamic_array - 1].dz
        z2d0b = -params.bridge_segments_array[dynamic_array - 1].dz
        # Zone 3
        z3d0l = -params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z3d0r = -params.bridge_segments_array[dynamic_array - 1].bz3 - params.bridge_segments_array[dynamic_array - 1].bz2 / 2
        z3d0t = 0
        z3d0b = -params.bridge_segments_array[dynamic_array - 1].dz

        ## D
        # Zone 1
        d1l = params.bridge_segments_array[dynamic_array].l + l_sum
        z1d1l = params.bridge_segments_array[dynamic_array].bz1 + params.bridge_segments_array[dynamic_array].bz2 / 2
        z1d1r = params.bridge_segments_array[dynamic_array].bz2 / 2
        z1d1t = 0
        z1d1b = -params.bridge_segments_array[dynamic_array].dz
        # Zone 2
        z2d1l = params.bridge_segments_array[dynamic_array].bz2 / 2
        z2d1r = -params.bridge_segments_array[dynamic_array].bz2 / 2
        z2d1t = params.bridge_segments_array[dynamic_array].dz_2 - params.bridge_segments_array[dynamic_array].dz
        z2d1b = -params.bridge_segments_array[dynamic_array].dz
        # Zone 3
        z3d1l = -params.bridge_segments_array[dynamic_array].bz2 / 2
        z3d1r = -params.bridge_segments_array[dynamic_array].bz3 - params.bridge_segments_array[dynamic_array].bz2 / 2
        z3d1t = 0
        z3d1b = -params.bridge_segments_array[dynamic_array].dz

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
            [255, clist[dynamic_array], clist[dynamic_array], 255],  # Box 1: Red
            [clist[dynamic_array], clist[dynamic_array], 255, 255],  # Box 2: Blue
            [clist[dynamic_array], 255, clist[dynamic_array], 255],  # Box 3: Green
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


def create_2d_top_view(viktor_params: Munch) -> dict:  # noqa: C901, PLR0912, PLR0915
    """
    Creates a 2D representation of the bridge top view, including lines, zone labels,
    and dimension lines with parameter values.

    Args:
        viktor_params (Munch): The VIKTOR parametrization object.
            - viktor_params.bridge_segments_array: List of Munch objects for each cross-section (this is the dynamic array).

    Returns:
        dict: A dictionary with "bridge_lines", "zone_annotations",
              "dimension_texts", and "cross_section_labels".

    """
    # Access the dynamic array data, which VIKTOR makes available
    # directly using the 'name' attribute given in the DynamicArray definition.
    try:
        segments_data = viktor_params.bridge_segments_array
        if segments_data is None:  # It might exist but be None if not filled
            segments_data = []
    except AttributeError:
        return {
            "bridge_lines": [],
            "zone_annotations": [],
            "dimension_texts": [],
            "cross_section_labels": [],
            "zone_polygons": [],
        }

    # Further ensure segments_data is a list, as DynamicArray can sometimes evaluate to None initially
    if not isinstance(segments_data, list):
        segments_data = []

    num_cross_sections = len(segments_data)

    if num_cross_sections < 1:  # Allow single cross-section for width dimensions
        return {
            "bridge_lines": [],
            "zone_annotations": [],
            "dimension_texts": [],
            "cross_section_labels": [],
            "zone_polygons": [],
        }

    bridge_lines = []
    zone_annotations = []
    dimension_texts_data = []
    cross_section_labels_data = []
    zone_polygons_data = []  # New list for zone background polygons
    current_x = 0.0
    # Determine max bridge height for positioning labels later
    max_y_top_outer = 0
    if segments_data:
        max_y_top_outer = max(seg.bz1 + seg.bz2 / 2.0 for seg in segments_data)
    label_y_offset = 0.5  # Reduced offset above the highest point for D labels

    def interpolate(y_start: float, y_end: float, factor: float = 0.5) -> float:
        return y_start + (y_end - y_start) * factor

    # --- Process Segments (for bridge lines, l-dimensions, and zone annotations) ---
    if num_cross_sections >= 2:
        for i in range(num_cross_sections - 1):
            seg_start_data = segments_data[i]
            seg_end_data = segments_data[i + 1]
            segment_length = seg_end_data.l
            next_x = current_x + segment_length
            bz1_start, bz2_start, bz3_start = seg_start_data.bz1, seg_start_data.bz2, seg_start_data.bz3
            half_bz2_start = bz2_start / 2.0
            y_top_outer_start = half_bz2_start + bz1_start
            y_top_inner_start = half_bz2_start
            y_bottom_inner_start = -half_bz2_start
            y_bottom_outer_start = -half_bz2_start - bz3_start
            bz1_end, bz2_end, bz3_end = seg_end_data.bz1, seg_end_data.bz2, seg_end_data.bz3
            half_bz2_end = bz2_end / 2.0
            y_top_outer_end = half_bz2_end + bz1_end
            y_top_inner_end = half_bz2_end
            y_bottom_inner_end = -half_bz2_end
            y_bottom_outer_end = -half_bz2_end - bz3_end
            segment_number = i + 1

            # Bridge Lines (copied from your previous version for completeness in this snippet)
            bridge_lines.append({"start": [current_x, y_top_outer_start], "end": [next_x, y_top_outer_end]})
            bridge_lines.append({"start": [current_x, y_top_inner_start], "end": [next_x, y_top_inner_end]})
            bridge_lines.append({"start": [current_x, y_bottom_inner_start], "end": [next_x, y_bottom_inner_end]})
            bridge_lines.append({"start": [current_x, y_bottom_outer_start], "end": [next_x, y_bottom_outer_end]})

            # --- Zone Background Polygons ---
            # Zone 1 Polygon (Red)
            zone1_vertices = [[current_x, y_top_inner_start], [next_x, y_top_inner_end], [next_x, y_top_outer_end], [current_x, y_top_outer_start]]
            zone_polygons_data.append(
                {
                    "zone_id": f"1-{segment_number}",
                    "vertices": zone1_vertices,
                    "color": "rgba(255, 0, 0, 0.15)",  # Light Red
                }
            )

            # Zone 2 Polygon (Blue) - only if it exists
            if bz2_start > 0 or bz2_end > 0:
                zone2_vertices = [
                    [current_x, y_bottom_inner_start],
                    [next_x, y_bottom_inner_end],
                    [next_x, y_top_inner_end],
                    [current_x, y_top_inner_start],
                ]
                zone_polygons_data.append(
                    {
                        "zone_id": f"2-{segment_number}",
                        "vertices": zone2_vertices,
                        "color": "rgba(0, 0, 255, 0.15)",  # Light Blue
                    }
                )

            # Zone 3 Polygon (Green)
            zone3_vertices = [
                [current_x, y_bottom_outer_start],
                [next_x, y_bottom_outer_end],
                [next_x, y_bottom_inner_end],
                [current_x, y_bottom_inner_start],
            ]
            zone_polygons_data.append(
                {
                    "zone_id": f"3-{segment_number}",
                    "vertices": zone3_vertices,
                    "color": "rgba(0, 255, 0, 0.15)",  # Light Green
                }
            )
            # --- End Zone Polygons ---

            # Zone Annotations (copied from your previous version for completeness)
            x_mid_segment = current_x + segment_length / 2.0
            y_top_outer_mid = interpolate(y_top_outer_start, y_top_outer_end)
            y_top_inner_mid = interpolate(y_top_inner_start, y_top_inner_end)
            y_bottom_inner_mid = interpolate(y_bottom_inner_start, y_bottom_inner_end)
            y_bottom_outer_mid = interpolate(y_bottom_outer_start, y_bottom_outer_end)
            y_mid_z1 = (y_top_outer_mid + y_top_inner_mid) / 2.0
            zone_annotations.append({"text": f"1-{segment_number}", "x": x_mid_segment, "y": y_mid_z1})
            if bz2_start > 0 or bz2_end > 0:
                y_mid_z2 = (y_top_inner_mid + y_bottom_inner_mid) / 2.0
                zone_annotations.append({"text": f"2-{segment_number}", "x": x_mid_segment, "y": y_mid_z2})
            y_mid_z3 = (y_bottom_inner_mid + y_bottom_outer_mid) / 2.0
            zone_annotations.append({"text": f"3-{segment_number}", "x": x_mid_segment, "y": y_mid_z3})

            # L-Dimension Text for this segment
            # Position it below the segment, aligned with its center
            l_text_y_offset = 1.0
            y_pos_for_l_text = min(y_bottom_outer_start, y_bottom_outer_end) - l_text_y_offset
            dimension_texts_data.append(
                {"text": f"l = {segment_length}m", "x": current_x + segment_length / 2.0, "y": y_pos_for_l_text, "type": "length", "textangle": 0}
            )

            current_x = next_x

    # --- Process Cross-Sections (for transverse bridge lines and bz-dimensions texts) ---
    cumulative_x = 0.0
    for j in range(num_cross_sections):
        cs_data = segments_data[j]
        if j > 0:
            cumulative_x += cs_data.l  # Use l from the current section for positioning the section line

        cs_x = cumulative_x  # This is the x-coordinate of the j-th cross-section line

        bz1, bz2, bz3 = cs_data.bz1, cs_data.bz2, cs_data.bz3
        half_bz2 = bz2 / 2.0
        y_top_outer = half_bz2 + bz1
        y_top_inner = half_bz2
        y_bottom_inner = -half_bz2
        y_bottom_outer = -half_bz2 - bz3

        # Transverse Bridge Lines for this cross-section (copied from previous version)
        bridge_lines.append({"start": [cs_x, y_top_outer], "end": [cs_x, y_top_inner]})
        bridge_lines.append({"start": [cs_x, y_bottom_inner], "end": [cs_x, y_bottom_outer]})
        if bz2 > 0:
            bridge_lines.append({"start": [cs_x, y_top_inner], "end": [cs_x, y_bottom_inner]})

        # BZ Dimension Texts for this cross-section
        text_x_offset = 0.75  # Increased offset to move text further left
        cross_section_number = j + 1  # 1-based index for labeling

        # bz1 text
        dimension_texts_data.append(
            {
                "text": f"bz 1-{cross_section_number}= {bz1}m",
                "x": cs_x - text_x_offset,
                "y": (y_top_inner + y_top_outer) / 2.0,
                "type": "width",
                "textangle": -90,
                "align": "center",
            }
        )

        # bz2 text
        if bz2 > 0:
            dimension_texts_data.append(
                {
                    "text": f"bz 2-{cross_section_number}= {bz2}m",
                    "x": cs_x - text_x_offset,
                    "y": (y_bottom_inner + y_top_inner) / 2.0,
                    "type": "width",
                    "textangle": -90,
                    "align": "center",
                }
            )

        # bz3 text
        dimension_texts_data.append(
            {
                "text": f"bz 3-{cross_section_number}= {bz3}m",
                "x": cs_x - text_x_offset,
                "y": (y_bottom_outer + y_bottom_inner) / 2.0,
                "type": "width",
                "textangle": -90,
                "align": "center",
            }
        )

        # Add D1, D2 labels above the cross-section line
        label_y_pos = max_y_top_outer + label_y_offset
        cross_section_labels_data.append({"text": f"D{cross_section_number}", "x": cs_x, "y": label_y_pos, "type": "cross_section_label"})

    return {
        "bridge_lines": bridge_lines,
        "zone_annotations": zone_annotations,
        "dimension_texts": dimension_texts_data,
        "cross_section_labels": cross_section_labels_data,
        "zone_polygons": zone_polygons_data,
    }
