"""Module for the Bridge entity controller."""


import trimesh
from viktor.core import File, ViktorController
from viktor.views import (
    GeometryResult,
    GeometryView,
)

from src.geometry.model_creator import (
    create_3d_model,  # Updated import
    create_cross_section,  # Import for cross-section creation
)

# Import parametrization from the separate file
from .parametrization import BridgeParametrization


class BridgeController(ViktorController):
    """Controller for the individual Bridge entity."""

    label = "Brug"
    parametrization = BridgeParametrization  # type: ignore[assignment] # Ignore potential complex assignment MyPy error

    @GeometryView("3D Model", duration_guess=1, x_axis_to_right=False)
    def get_3d_view(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """Generates a 3D representation of the bridge deck."""
        combined_scene = create_3d_model(params)
        # Export the scene as a GLTF file and return it as a GeometryResult
        geometry = File()
        with geometry.open_binary() as w:
            w.write(trimesh.exchange.gltf.export_glb(combined_scene))
        return GeometryResult(geometry, geometry_type="gltf")


    @GeometryView("Bovenaanzicht", duration_guess=1, x_axis_to_right=True)
    def get_top_view(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """
        Generates a top view of the bridge deck by slicing the 3D model with a horizontal plane.

        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            GeometryResult: A 2D representation of the top view in GLTF format.

        """
        # Generate the 3D model
        scene = create_3d_model(params)
        combined_mesh = trimesh.util.concatenate(scene.geometry.values())

        # Define the slicing plane (horizontal plane at z=0)
        plane_origin = [0, 0, params.input.dimensions.top_view_loc]  # Origin of the plane
        plane_normal = [0, 0, 1]  # Normal vector of the plane (z-axis)

        # Create the cross-section
        combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

        geometry = File()
        with geometry.open_binary() as w:
            w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
        return GeometryResult(geometry, geometry_type="gltf")


    @GeometryView("Langsdoorsnede", duration_guess=1, x_axis_to_right=True)
    def get_longitudinal_section(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """
        Generates a longitudinal section of the bridge deck by slicing the 3D model with a vertical plane.

        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            GeometryResult: A 2D representation of the longitudinal section in GLTF format.

        """
        # Generate the 3D model
        scene = create_3d_model(params)
        combined_mesh = trimesh.util.concatenate(scene.geometry.values())

        # Define the slicing plane (horizontal plane at y=0)
        plane_origin = [0, params.input.dimensions.longitudinal_section_loc, 0]  # Origin of the plane
        plane_normal = [0, 1, 0]  # Normal vector of the plane (y-axis)

        # Create the cross-section
        combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

        geometry = File()
        with geometry.open_binary() as w:
            w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
        return GeometryResult(geometry, geometry_type="gltf")

    @GeometryView("Dwarsdoorsnede", duration_guess=1, x_axis_to_right=True)
    def get_cross_section(self, params: BridgeParametrization, **kwargs) -> GeometryResult:  # noqa: ARG002
        """
        Generates a cross-section of the bridge deck by slicing the 3D model with a vertical plane perpendicular to the longitudinal axis.

        Args:
            params (BridgeParametrization): Input parameters for the bridge dimensions.
            **kwargs: Additional arguments.

        Returns:
            GeometryResult: A 2D representation of the cross-section in GLTF format.

        """
        # Generate the 3D model
        scene = create_3d_model(params)
        combined_mesh = trimesh.util.concatenate(scene.geometry.values())

        # Define the slicing plane (horizontal plane at x=0)
        plane_origin = [params.input.dimensions.cross_section_loc, 0, 0]  # Origin of the plane
        plane_normal = [1, 0, 0]  # Normal vector of the plane (x-axis)

        # Create the cross-section
        combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

        geometry = File()
        with geometry.open_binary() as w:
            w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
        return GeometryResult(geometry, geometry_type="gltf")



