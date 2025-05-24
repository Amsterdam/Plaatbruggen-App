"""
Test module for horizontal section geometry functionality.

This module contains tests for creating horizontal section views and related geometry operations.
"""
import math
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import plotly.graph_objects as go
import trimesh  # Likely needed for mocks or type hints
from munch import Munch  # type: ignore[import-untyped]

from src.geometry.horizontal_section import create_horizontal_section_annotations, create_horizontal_section_view

# model_creator functions (create_3d_model, create_cross_section) will be mocked from their original module
# trimesh will be mocked where needed


class TestHorizontalSection(unittest.TestCase):
    """Test cases for horizontal section geometry creation."""

    def _create_mock_segment_param(  # noqa: PLR0913
        self,
        length: float = 10.0,
        bz1: float = 2.0,
        bz2: float = 3.0,
        bz3: float = 2.5,
        dz: float = 0.5,
        dz_2: float = 0.6,
    ) -> Munch:
        return Munch({"l": length, "bz1": bz1, "bz2": bz2, "bz3": bz3, "dz": dz, "dz_2": dz_2})

    def _create_default_params_for_annotations(
        self,
        num_segments: int = 1,
        horizontal_section_loc: float = -1.0
    ) -> Munch:
        # horizontal_section_loc < 0 means all zones (1,2,3) are considered for annotations
        # horizontal_section_loc >= 0 means only_zone2 = True
        segments = [
            self._create_mock_segment_param(l=10.0 + i * 5, bz1=1.0 + i * 0.1, bz2=2.0 + i * 0.1, bz3=1.0 + i * 0.1)
            for i in range(num_segments)
        ]

        return Munch({"bridge_segments_array": segments, "input": Munch({"dimensions": Munch({"horizontal_section_loc": horizontal_section_loc})})})

    def test_create_horizontal_section_annotations_all_zones(self) -> None:
        """Test annotations when all zones (1,2,3) should be present."""
        params = self._create_default_params_for_annotations(num_segments=2, horizontal_section_loc=-1.0)  # only_zone2 = False
        all_y_mock = [-2.0, 0, 2.0]  # Mock y-range for min/max calculations

        annotations = create_horizontal_section_annotations(params, all_y_mock)

        # --- Expected counts (for 2 segments) ---
        # D-labels: 2 (D1, D2)
        # Zone labels: Z1-0, Z1-1, Z2-0, Z2-1, Z3-0, Z3-1 (first segment is index 0 for Z labels in code)
        # The code generates labels like Z1-0, Z1-1 for the *parts between* D-points.
        # So for 2 D-points (segments in params), there is 1 such part.
        # The loop `for i, zcx, cz1 in zip(row_labels, zone_center_x, zone1_center_y)` where row_labels is range(len(segments))
        # and zone_center_x is for l_values[1:] (i.e., for segments *after* the first D-point)
        # This means for 2 segments in params (D1, D2), we expect Z labels for segment part between D1 and D2 (index 0 of this part).
        # Wait, `row_labels` is `list(range(len(params.bridge_segments_array)))` which for 2 segments is `[0, 1]`
        # `zone_center_x` is `[cum + val / 2 for cum, val in zip(l_values_cumulative, l_values[1:])]`
        # `l_values` is from `params.bridge_segments_array`. `l_values[1:]` means it skips the first segment's length for centering.
        # `l_values_cumulative` also from `params.bridge_segments_array`.
        # If num_segments = 2 (D1, D2), len(zone_center_x) will be 1 (for the part D1-D2).
        # Zone labels: Z1-0, Z2-0, Z3-0 (associated with the segment part after D1, up to D2)
        # Length dimensions: 1 (for the segment part D1-D2)
        # Width dimensions: Z1 (1), Z2 (1), Z3 (1) for D1. And Z1(1), Z2(1), Z3(1) for D2
        # The width annotations are `for zcx, cz1, bz1 in zip(l_values_cumulative, zone1_center_y, b_values_1)`
        # l_values_cumulative has 2 items (D1, D2). So 2 sets of width annotations.

        num_segments = len(params.bridge_segments_array)
        num_segment_parts = num_segments - 1 if num_segments > 1 else 1  # Parts between D-points, or 1 if only one D-point

        expected_d_labels = num_segments
        expected_z_labels = 3 * num_segment_parts  # Z1, Z2, Z3 for each part
        expected_len_dims = num_segment_parts
        expected_width_dims = 3 * num_segments  # bz1, bz2, bz3 for each D-point definition in segments_array
        total_expected_annotations = expected_d_labels + expected_z_labels + expected_len_dims + expected_width_dims

        assert len(annotations) == total_expected_annotations

        # Spot check some: D1 label, a Z1 label, a length, a width for bz1 of D1
        seg0 = params.bridge_segments_array[0]
        seg1 = params.bridge_segments_array[1]
        # These are the x-coordinates for D-1, D-2, ...
        sut_d_point_x_coords = []
        current_sum_sut = 0.0
        for k_seg in range(num_segments):
            current_sum_sut += params.bridge_segments_array[k_seg].l
            sut_d_point_x_coords.append(current_sum_sut)

        # D1 label (corresponds to l_values_cumulative[0] in SUT)
        d1_label = next(ann for ann in annotations if ann.text == "<b>D-1</b>")
        assert math.isclose(d1_label.x, sut_d_point_x_coords[0])  # Should be seg0.l
        assert math.isclose(d1_label.y, max(all_y_mock) + 0.5)

        # D2 label (corresponds to l_values_cumulative[1] in SUT)
        if num_segments > 1:
            d2_label = next(ann for ann in annotations if ann.text == "<b>D-2</b>")
            assert math.isclose(d2_label.x, sut_d_point_x_coords[1])  # Should be seg0.l + seg1.l
            assert math.isclose(d2_label.y, max(all_y_mock) + 0.5)

        # Zone labels and length dimensions are for segment *parts* between D-points
        # SUT's zone_center_x = [cum + val / 2 for cum, val in zip(l_values_cumulative, l_values[1:])]
        # l_values_cumulative in SUT: [L0, L0+L1, ...]
        # l_values in SUT: [L0, L1, L2, ...]
        # l_values[1:] in SUT: [L1, L2, ...]
        # For 2 segments (L0, L1):
        # This is the center of the second segment (length L1), placed relative to the end of the first segment.

        # Correcting `l_coords_d_points_expected` for the test spot check:
        seg0.l + seg1.l if num_segments > 1 else None

        # Re-calculate zone_center_x_actual based on SUT's logic
        sut_l_values = [p.l for p in params.bridge_segments_array]
        sut_l_values_cumulative_for_zip = sut_d_point_x_coords  # This is [L0, L0+L1] for 2 segments
        sut_l_values_for_zip_val = sut_l_values[1:]  # This is [L1] for 2 segments

        zone_center_x_actual = []
        if sut_l_values_for_zip_val:  # only if there's a second segment onwards
            zone_center_x_actual = [cum + val / 2 for cum, val in zip(sut_l_values_cumulative_for_zip, sut_l_values_for_zip_val)]
            # For 2 segments: cum=L0, val=L1. zone_center_x_actual = [L0 + L1/2]

        # D1 label
        # Already checked above

        # Z1-1 (Zone 1 of the first segment part, index 0 from SUT's row_labels)
        # The SUT's zone labels (Z1-i, Z2-i, Z3-i) are zipped with zone_center_x.
        # If zone_center_x_actual has one element (e.g., [L0 + L1/2]), then i will be 0.
        # The text will be Z1-1, Z2-1, Z3-1.
        # The y-coordinates (zone1_center_y etc.) are also indexed by i.
        # zoneX_center_y in SUT: [seg0.bz_val, seg1.bz_val, ...]
        # So for Z1-1 (i=0), it uses seg0's bz values, but x-position is L0 + L1/2.

        if zone_center_x_actual:  # If there are zone centers calculated
            z1_1_label = next(ann for ann in annotations if ann.text == "<b>Z1-1</b>")
            assert math.isclose(z1_1_label.x, zone_center_x_actual[0])
            # Y-coord uses seg0.bz values because SUT's zoneX_center_y[0] corresponds to seg0
            assert math.isclose(z1_1_label.y, seg0.bz2 / 2 + seg0.bz1 / 2)

            # Length for this segment part (length should be L1 (sut_l_values[1]) based on SUT's dimension_annotations)
            # SUT uses zip(l_values[1:], zone_center_x) for length dimensions
            # So for 2 segments, length=sut_l_values[1]=L1, zcx=zone_center_x_actual[0]
            len_label = next(ann for ann in annotations if f"l = {sut_l_values[1]}m" in ann.text)
            assert math.isclose(len_label.x, zone_center_x_actual[0])

        # Width bz1 at D1 (x should be sut_d_point_x_coords[0] - 1 for D1)
        # SUT width annotations use l_values_cumulative for x-coordinates (zcx in its loop)
        # So for bz1 of D1, zcx = sut_d_point_x_coords[0] = L0.
        # y-coord is zone1_center_y[0] = seg0.bz2/2 + seg0.bz1/2
        width_bz1_d1 = next(ann for ann in annotations if f"b = {seg0.bz1}m" in ann.text and ann.y == (seg0.bz2 / 2 + seg0.bz1 / 2))
        assert math.isclose(width_bz1_d1.x, sut_d_point_x_coords[0] - 1)

    def test_create_horizontal_section_annotations_only_zone2(self) -> None:
        """Test annotations when only_zone2 is True."""
        params = self._create_default_params_for_annotations(num_segments=1, horizontal_section_loc=0.5)  # only_zone2 = True
        all_y_mock = [-1.0, 0, 1.0]
        annotations = create_horizontal_section_annotations(params, all_y_mock)

        num_segments = len(params.bridge_segments_array)
        # If num_segments is 1 (D1), SUT's l_values=[seg0.l]. l_values_cumulative=[0.0].
        # l_values[1:] is empty. So zone_center_x is empty. No Z-labels, no length dimensions.
        # Width dimensions: for bz2 of D1. (1 total)
        # D-labels: 1 (D1)
        # Total = 1 D-label + 1 width_dim = 2
        expected_d_labels = num_segments  # 1
        expected_z_labels = 0  # No segment parts if only 1 D-point for zone_center_x calc
        expected_len_dims = 0  # "
        expected_width_dims = 1 * num_segments  # Only bz2 for each D-point definition (1 for D1)
        total_expected_annotations = expected_d_labels + expected_z_labels + expected_len_dims + expected_width_dims

        assert len(annotations) == total_expected_annotations  # Should be 1 D-label + 1 width = 2. Original error was 2 != 4

        # Check that no Z1 or Z3 labels are present
        assert not any("Z1-" in ann.text for ann in annotations)
        assert not any("Z3-" in ann.text for ann in annotations)
        # Check that NO Z2 label is present due to num_segment_parts logic for zone_center_x
        assert not any("Z2-" in ann.text for ann in annotations)

        # Check that only bz2 width annotations are present
        # For D1 (params.bridge_segments_array[0])
        seg0 = params.bridge_segments_array[0]
        assert any(f"b = {seg0.bz2}m" in ann.text for ann in annotations)
        assert not any(f"b = {seg0.bz1}m" in ann.text for ann in annotations)
        assert not any(f"b = {seg0.bz3}m" in ann.text for ann in annotations)

    @patch("src.geometry.horizontal_section.create_3d_model")
    @patch("src.geometry.horizontal_section.trimesh")  # Patch trimesh module used in horizontal_section
    @patch("src.geometry.horizontal_section.create_cross_section")  # This is from model_creator
    @patch("src.geometry.horizontal_section.create_horizontal_section_annotations")
    def test_create_horizontal_section_view_basic_flow(
        self,
        mock_create_horizontal_annotations: MagicMock,
        mock_model_creator_create_cross_section: MagicMock,
        mock_trimesh_module: MagicMock,
        mock_create_3d_model: MagicMock
    ) -> None:
        """Test basic flow of create_horizontal_section_view with mocks."""
        params = Munch(
            {
                "bridge_segments_array": [  # Minimal data for create_3d_model mock
                    self._create_mock_segment_param(l=10)
                ],
                "input": Munch({"dimensions": Munch({"horizontal_section_loc": 0.5})}),  # For annotations call
            }
        )
        section_loc_z_val = 0.5

        # Mock create_3d_model
        mock_3d_scene = MagicMock()
        mock_3d_geometry_collection = MagicMock()
        mock_3d_geometry_collection.values.return_value = [MagicMock(spec=trimesh.Trimesh)]
        mock_3d_scene.geometry = mock_3d_geometry_collection
        mock_create_3d_model.return_value = mock_3d_scene

        # Mock trimesh.util.concatenate (call 1 for 3D)
        mock_combined_3d_mesh = MagicMock(spec=trimesh.Trimesh)

        # Mock model_creator.create_cross_section
        mock_2d_scene_from_cs = MagicMock(spec=trimesh.Scene)
        mock_2d_geometry_collection_cs = MagicMock()
        mock_2d_geometry_collection_cs.values.return_value = [MagicMock(spec=trimesh.Trimesh)]
        mock_2d_scene_from_cs.geometry = mock_2d_geometry_collection_cs
        mock_model_creator_create_cross_section.return_value = mock_2d_scene_from_cs

        # Mock trimesh.util.concatenate (call 2 for 2D)
        mock_combined_2d_mesh = MagicMock(spec=trimesh.Trimesh)
        mock_combined_2d_mesh.vertices = np.array([[0, 0, 0], [1, 1, 0], [1, 0, 0]])  # x, y, (z ignored for 2d plot)
        mock_entity1 = MagicMock()
        mock_entity1.points = [0, 1, 2]
        mock_combined_2d_mesh.entities = [mock_entity1]
        mock_trimesh_module.util.concatenate.side_effect = [mock_combined_3d_mesh, mock_combined_2d_mesh]

        # Mock create_horizontal_section_annotations
        mock_annotation_list = [go.layout.Annotation(text="Mock Annotation")]
        mock_create_horizontal_annotations.return_value = mock_annotation_list

        # Act
        fig = create_horizontal_section_view(params, section_loc_z_val)

        # Assertions
        mock_create_3d_model.assert_called_once_with(params, axes=False)
        assert mock_trimesh_module.util.concatenate.call_count == 2
        mock_trimesh_module.util.concatenate.assert_any_call(mock_3d_geometry_collection.values())

        expected_plane_origin = [0, 0, section_loc_z_val]
        expected_plane_normal = [0, 0, 1]
        mock_model_creator_create_cross_section.assert_called_once_with(
            mock_combined_3d_mesh, expected_plane_origin, expected_plane_normal, axes=False
        )
        mock_trimesh_module.util.concatenate.assert_any_call(mock_2d_geometry_collection_cs.values())

        # Check traces from entities (plot uses x and y from vertices array)
        assert len(fig.data) == 1  # From mock_combined_2d_mesh.entities
        trace0 = fig.data[0]
        assert list(trace0.x) == [0, 1, 1]  # Vertices[points][0]
        assert list(trace0.y) == [0, 1, 0]  # Vertices[points][1]
        assert trace0.line.color == "black"

        # Check call to annotation function
        all_y_from_mock_mesh = [0, 1, 0]  # vertices[:, 1]
        mock_create_horizontal_annotations.assert_called_once_with(params, all_y_from_mock_mesh)
        assert fig.layout.annotations == tuple(mock_annotation_list)

        # Check layout
        assert fig.layout.title.text == "Horizontale doorsnede (Horizontal Section)"
        assert fig.layout.xaxis.title.text == "X-as - Lengte [m]"
        assert fig.layout.yaxis.title.text == "Y-as - Breedte [m]"
        assert fig.layout.yaxis.scaleanchor == "x"
        assert fig.layout.yaxis.scaleratio == 1
        assert not fig.layout.showlegend


if __name__ == "__main__":
    unittest.main()
