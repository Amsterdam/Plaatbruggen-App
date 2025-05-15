    # @GeometryView("3D - Horizontale doorsnede", duration_guess=1, x_axis_to_right=True)
    # def get_3d_horizontal_section(self, params: BridgeParametrization, **kwargs) -> GeometryResult:
    #     """
    #     Generates a horizontal section of the bridge deck by slicing the 3D model with a horizontal plane.

    #     This function creates a 2D representation of the bridge's horizontal section by:
    #     1. Creating a 3D model of the bridge
    #     2. Slicing it with a horizontal plane at the specified height
    #     3. Converting the resulting section into a 2D view showing length (x) vs width (y)

    #     Args:
    #         params (BridgeParametrization): Input parameters for the bridge dimensions.
    #         **kwargs: Additional arguments.

    #     Returns:
    #         GeometryResult: A 2D representation of the horizontal section in GLTF format.
    #     """
    #     # Generate the 3D model
    #     scene = create_3d_model(params)
    #     combined_mesh = trimesh.util.concatenate(scene.geometry.values())

    #     # Define the slicing plane for the horizontal section
    #     # The plane is horizontal (normal to z-axis) at the specified height
    #     plane_origin = [0, 0, params.input.dimensions.horizontal_section_loc]
    #     plane_normal = [0, 0, 1]

    #     # Create the section by slicing the 3D model
    #     combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

    #     # Export the section as a GLTF file
    #     geometry = File()
    #     with geometry.open_binary() as w:
    #         w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
    #     return GeometryResult(geometry, geometry_type="gltf")

    # @GeometryView("3D - Langsdoorsnede", duration_guess=1, x_axis_to_right=True)
    # def get_3d_longitudinal_section(self, params: BridgeParametrization, **kwargs) -> GeometryResult:
    #     """
    #     Generates a longitudinal section of the bridge deck by slicing the 3D model with a vertical plane.

    #     Args:
    #         params (BridgeParametrization): Input parameters for the bridge dimensions.
    #         **kwargs: Additional arguments.

    #     Returns:
    #         GeometryResult: A 2D representation of the longitudinal section in GLTF format.

    #     """
    #     # Generate the 3D model
    #     scene = create_3d_model(params)
    #     combined_mesh = trimesh.util.concatenate(scene.geometry.values())

    #     # Define the slicing plane (horizontal plane at y=0)
    #     plane_origin = [0, params.input.dimensions.longitudinal_section_loc, 0]  # Origin of the plane
    #     plane_normal = [0, 1, 0]  # Normal vector of the plane (y-axis)

    #     # Create the cross-section
    #     combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

    #     geometry = File()
    #     with geometry.open_binary() as w:
    #         w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
    #     return GeometryResult(geometry, geometry_type="gltf")

    # @GeometryView("3D - Dwarsdoorsnede", duration_guess=1, x_axis_to_right=True)
    # def get_3d_cross_section(self, params: BridgeParametrization, **kwargs) -> GeometryResult:
    #     """
    #     Generates a cross-section of the bridge deck by slicing the 3D model with a vertical plane perpendicular to the longitudinal axis.

    #     Args:
    #         params (BridgeParametrization): Input parameters for the bridge dimensions.
    #         **kwargs: Additional arguments.

    #     Returns:
    #         GeometryResult: A 2D representation of the cross-section in GLTF format.

    #     """
    #     # Generate the 3D model
    #     scene = create_3d_model(params)
    #     combined_mesh = trimesh.util.concatenate(scene.geometry.values())

    #     # Define the slicing plane (horizontal plane at x=0)
    #     plane_origin = [params.input.dimensions.cross_section_loc, 0, 0]  # Origin of the plane
    #     plane_normal = [1, 0, 0]  # Normal vector of the plane (x-axis)

    #     # Create the cross-section
    #     combined_scene_2d = create_cross_section(combined_mesh, plane_origin, plane_normal)

    #     geometry = File()
    #     with geometry.open_binary() as w:
    #         w.write(trimesh.exchange.gltf.export_glb(combined_scene_2d))
    #     return GeometryResult(geometry, geometry_type="gltf")
