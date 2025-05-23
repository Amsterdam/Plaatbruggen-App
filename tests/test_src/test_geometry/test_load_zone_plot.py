import unittest
from typing import Any
from unittest.mock import patch

import numpy as np
import plotly.graph_objects as go
from munch import Munch  # type: ignore[import-untyped]

from src.geometry.load_zone_geometry import LoadZoneDataRow  # For constructing test data
from src.geometry.load_zone_plot import (
    DEFAULT_PLOTLY_COLORS,
    DEFAULT_ZONE_APPEARANCE_MAP,
    # TypedDicts - will be used for constructing test data
    BridgeBaseGeometry,
    PlotPresentationDetails,
    ZoneBoundaryLineStyle,
    ZonePlottingGeometry,
    ZoneStylingDefaults,
    build_load_zones_figure,
    create_zone_boundary_line_traces,
    create_zone_fill_trace,
    create_zone_main_label_annotation,
    create_zone_width_annotations,  # Assuming this will be fully tested
    get_zone_appearance_properties,
)


class TestLoadZonePlotHelpers(unittest.TestCase):
    """Tests for helper functions in load_zone_plot.py."""

    def test_get_zone_appearance_properties_default(self):
        props = get_zone_appearance_properties("UnknownType", 0)
        self.assertEqual(props["line_color"], DEFAULT_PLOTLY_COLORS[0])
        self.assertTrue(props["fill_color"].startswith("rgba"))
        self.assertEqual(props["pattern_shape"], "")

    def test_get_zone_appearance_properties_known_type(self):
        props = get_zone_appearance_properties("Voetgangers", 0)
        self.assertEqual(props["line_color"], DEFAULT_ZONE_APPEARANCE_MAP["Voetgangers"]["line_color"])
        self.assertEqual(props["fill_color"], DEFAULT_ZONE_APPEARANCE_MAP["Voetgangers"]["fill_color"])
        self.assertEqual(props["pattern_shape"], DEFAULT_ZONE_APPEARANCE_MAP["Voetgangers"]["pattern_shape"])

    def test_get_zone_appearance_properties_exceeding_limits(self):
        props = get_zone_appearance_properties("AnyType", 0, is_exceeding_limits=True)
        self.assertEqual(props["line_color"], "red")
        self.assertEqual(props["fill_color"], "rgba(255, 0, 0, 0.3)")
        self.assertEqual(props["pattern_shape"], "x")

    def test_create_zone_fill_trace_valid_data(self):
        trace = create_zone_fill_trace(
            x_coords=[0, 1, 1, 0],
            y_coords_top=[1, 1, 1, 1],
            y_coords_bottom=[0, 0, 0, 0],
            appearance_props={"fill_color": "blue", "pattern_shape": "+", "pattern_fgcolor": "red", "pattern_solidity": 0.5},
        )
        self.assertIsNotNone(trace)
        assert trace is not None  # for mypy
        self.assertEqual(trace.fillpattern.shape, "+")
        self.assertEqual(trace.fillpattern.fgcolor, "red")
        self.assertEqual(trace.fillpattern.solidity, 0.5)

    def test_create_zone_fill_trace_empty_data(self):
        trace = create_zone_fill_trace([], [], [], {})
        self.assertIsNone(trace)

    def test_create_zone_boundary_line_traces_first_zone(self):
        geometry = ZonePlottingGeometry(x_coords=[0, 1], y_coords_top=[1, 1], y_coords_bottom=[0, 0])
        style = ZoneBoundaryLineStyle(line_color="green", sbs_line_thickness=1, sbs_offset=0.1, absolute_edge_thickness=3)
        traces = create_zone_boundary_line_traces(0, 3, geometry, style)  # zone_idx 0, 3 total zones
        self.assertEqual(len(traces), 2)
        # Top line (absolute edge)
        self.assertEqual(traces[0].line.width, 3)
        self.assertEqual(list(traces[0].y), [1, 1])
        # Bottom line (shared, offset)
        self.assertEqual(traces[1].line.width, 1)
        self.assertEqual(list(traces[1].y), [0 + 0.1, 0 + 0.1])  # y + sbs_offset

    def test_create_zone_boundary_line_traces_middle_zone(self):
        geometry = ZonePlottingGeometry(x_coords=[0, 1], y_coords_top=[2, 2], y_coords_bottom=[1, 1])
        style = ZoneBoundaryLineStyle(line_color="blue", sbs_line_thickness=1, sbs_offset=0.1, absolute_edge_thickness=3)
        traces = create_zone_boundary_line_traces(1, 3, geometry, style)  # zone_idx 1, 3 total zones
        self.assertEqual(len(traces), 2)
        # Top line (shared, offset)
        self.assertEqual(traces[0].line.width, 1)
        self.assertEqual(list(traces[0].y), [2 - 0.1, 2 - 0.1])  # y - sbs_offset
        # Bottom line (shared, offset)
        self.assertEqual(traces[1].line.width, 1)
        self.assertEqual(list(traces[1].y), [1 + 0.1, 1 + 0.1])  # y + sbs_offset

    def test_create_zone_boundary_line_traces_last_zone(self):
        geometry = ZonePlottingGeometry(x_coords=[0, 1], y_coords_top=[3, 3], y_coords_bottom=[2, 2])
        style = ZoneBoundaryLineStyle(line_color="purple", sbs_line_thickness=1, sbs_offset=0.1, absolute_edge_thickness=3)
        traces = create_zone_boundary_line_traces(2, 3, geometry, style)  # zone_idx 2, 3 total zones
        self.assertEqual(len(traces), 2)
        # Top line (shared, offset)
        self.assertEqual(traces[0].line.width, 1)
        self.assertEqual(list(traces[0].y), [3 - 0.1, 3 - 0.1])  # y - sbs_offset
        # Bottom line (absolute edge)
        self.assertEqual(traces[1].line.width, 3)
        self.assertEqual(list(traces[1].y), [2, 2])

    def test_create_zone_main_label_annotation(self):
        geometry = ZonePlottingGeometry(x_coords=[0, 10, 20], y_coords_top=[5, 5, 5], y_coords_bottom=[4, 4, 4])
        annotation = create_zone_main_label_annotation(0, "TestZone", geometry, x_offset=1.0)
        self.assertIsInstance(annotation, go.layout.Annotation)
        self.assertEqual(annotation.x, 20 + 1.0)  # x_coord_at_end + x_offset
        self.assertEqual(annotation.y, (5 + 4) / 2)  # Midpoint of y_top_end and y_bottom_end
        self.assertEqual(annotation.text, "<b>bz1</b>: <i>TestZone</i>")

    def test_create_zone_width_annotations_basic(self):
        zone_param_data = self._create_dummy_load_zone_data_row(d_widths=[2.0, 2.5, 3.0])
        geometry = ZonePlottingGeometry(
            x_coords=[0.0, 10.0, 20.0],  # D1, D2, D3 x-coords
            y_coords_top=[1.0, 1.1, 1.2],
            y_coords_bottom=[0.0, 0.1, 0.2],
        )
        num_defined_d_points = 3
        zone_idx = 0
        num_load_zones = 2

        annotations = create_zone_width_annotations(zone_param_data, geometry, num_defined_d_points, zone_idx, num_load_zones)
        self.assertEqual(len(annotations), 3)

        # Check annotation for d_idx = 0 (D1, width 2.0m)
        ann_d0 = next(ann for ann in annotations if ann.x == geometry["x_coords"][0])
        self.assertEqual(ann_d0.text, "2.00m")

        # Check annotation for d_idx = 1 (D2, width 2.5m)
        ann_d1 = next(ann for ann in annotations if ann.x == geometry["x_coords"][1])
        self.assertEqual(ann_d1.text, "2.50m")

        # Check annotation for d_idx = 2 (D3, width 3.0m)
        ann_d2 = next(ann for ann in annotations if ann.x == geometry["x_coords"][2])
        self.assertEqual(ann_d2.text, "3.00m")

    def test_create_zone_width_annotations_last_zone_uses_calculated_width(self):
        # For the last zone, display_width should be the calculated current_zone_calculated_width
        zone_param_data = self._create_dummy_load_zone_data_row(d_widths=[2.0, 2.0])  # Params might suggest 2.0
        geometry = ZonePlottingGeometry(
            x_coords=[0, 10],
            y_coords_top=[3, 3],
            y_coords_bottom=[1.5, 1.2],  # Calculated widths: 1.5, 1.8
        )
        annotations = create_zone_width_annotations(zone_param_data, geometry, 2, 0, 1)  # Last zone (idx 0 of 1)
        self.assertEqual(len(annotations), 2)
        self.assertEqual(annotations[0].text, "1.50m")  # Calculated width
        self.assertEqual(annotations[1].text, "1.80m")  # Calculated width

    def test_create_zone_width_annotations_empty_if_widths_too_small(self):
        zone_param_data = self._create_dummy_load_zone_data_row(d_widths=[0.001, 0.002])
        geometry = ZonePlottingGeometry(x_coords=[0, 1], y_coords_top=[1, 1], y_coords_bottom=[0.999, 0.998])
        annotations = create_zone_width_annotations(zone_param_data, geometry, 2, 0, 1)
        self.assertEqual(len(annotations), 0)

    def _create_dummy_load_zone_data_row(self, d_widths: list[float]) -> LoadZoneDataRow:
        """Creates a LoadZoneDataRow-like dictionary for testing width annotations."""
        row_dict: dict[str, Any] = {"zone_type": "Dummy"}  # zone_type not used by create_zone_width_annotations
        for i, width in enumerate(d_widths):
            row_dict[f"d{i + 1}_width"] = width  # Store raw float, not Munch(value=width)
        # Fill remaining up to 15 with 0.0 if not provided
        for i in range(len(d_widths) + 1, 16):
            row_dict[f"d{i}_width"] = 0.0
        return row_dict  # type: ignore


class TestBuildLoadZonesFigure(unittest.TestCase):
    """Tests for the main build_load_zones_figure function."""

    def _create_minimal_load_zone_data_row(self, zone_type="Auto", d_widths=None) -> LoadZoneDataRow:
        if d_widths is None:
            # Ensure d_widths matches num_defined_d_points in BridgeBaseGeometry for simplicity
            d_widths = [1.0] * 5  # Example: 5 D-points

        # Create a dictionary that matches the structure of LoadZoneDataRow
        # We use Munch here for dot-notation access similar to how params might be structured
        row_dict: dict[str, Any] = {
            "zone_type": Munch(value=zone_type),  # Assuming zone_type is a field with a .value
            "is_exceeding_limits": False,
            # Add the keys that the SUT expects
            "zone_widths_per_d": d_widths,  # list[float] that the SUT expects
            "y_coords_top_current_zone": [2.0] * len(d_widths),  # Mock top coordinates
            # Add all dX_width fields, e.g., d1_width, d2_width...
            # Based on a max of 15 D-fields from other context
        }
        for i in range(1, 16):
            row_dict[f"d{i}_width"] = Munch(value=d_widths[i - 1] if i <= len(d_widths) else 0.0)

        # Cast to LoadZoneDataRow (which is a TypedDict)
        # This step is more for type checking during test writing;
        # the function itself will receive a list of such dictionaries (or Munch objects)
        return row_dict  # type: ignore

    def _get_default_bridge_base_geometry(self, num_d_points=5) -> BridgeBaseGeometry:
        # y_coords_bridge_bottom_edge should be list[list[float]], e.g., [[y_min, y_max], ...]
        # Let's assume y_min_bridge_at_d_point = -5.0 and y_max_bridge_at_d_point = 5.0 for testing
        y_min_val = -5.0
        y_max_val = 5.0  # This would be from y_coords_bridge_top_edge generally
        return BridgeBaseGeometry(
            x_coords_d_points=list(np.linspace(0, 20, num_d_points)),
            y_coords_bridge_top_edge=[y_max_val] * num_d_points,  # Consistent with y_max_val. This is a list[float]
            y_coords_bridge_bottom_edge=[[y_min_val, y_max_val] for _ in range(num_d_points)],  # This is list[list[float]]
            num_defined_d_points=num_d_points,
        )

    def _get_default_styling_defaults(self) -> ZoneStylingDefaults:
        return ZoneStylingDefaults(
            zone_appearance_map=DEFAULT_ZONE_APPEARANCE_MAP,
            default_plotly_colors=DEFAULT_PLOTLY_COLORS,
        )

    def _get_default_presentation_details(self) -> PlotPresentationDetails:
        return PlotPresentationDetails(
            base_traces=None,
            validation_messages=None,
            figure_title="Test Load Zones Plot",
        )

    @patch("src.geometry.load_zone_plot.calculate_zone_bottom_y_coords")
    @patch("src.geometry.load_zone_plot.get_zone_appearance_properties")
    @patch("src.geometry.load_zone_plot.create_zone_fill_trace")
    @patch("src.geometry.load_zone_plot.create_zone_boundary_line_traces")
    @patch("src.geometry.load_zone_plot.create_zone_main_label_annotation")
    @patch("src.geometry.load_zone_plot.create_zone_width_annotations")
    def test_build_load_zones_figure_single_zone_no_warnings(
        self,
        mock_create_width_annots,
        mock_create_main_label,
        mock_create_boundary_lines,
        mock_create_fill_trace,
        mock_get_appearance,
        mock_calculate_bottom_y,
    ):
        """Test with a single load zone and no validation warnings."""
        num_d_points = 3
        bridge_geom = self._get_default_bridge_base_geometry(num_d_points=num_d_points)

        # Mock return values for helpers
        # y_coords_top_of_current_zone and y_coords_bottom_of_current_zone are list[float]
        def debug_mock(zone_idx, num_load_zones, num_defined_d_points, y_coords_top, y_bridge_bottom, zone_params):
            return [0.0] * num_defined_d_points  # Return list[float], not tuple

        mock_calculate_bottom_y.side_effect = debug_mock
        mock_get_appearance.return_value = {"line_color": "blue", "fill_color": "lightblue", "pattern_shape": ""}
        mock_create_fill_trace.return_value = go.Scatter(name="mock_fill_trace")
        mock_create_boundary_lines.return_value = [go.Scatter(name="mock_boundary_trace")]
        mock_create_main_label.return_value = go.layout.Annotation(text="mock_label")
        mock_create_width_annots.return_value = [go.layout.Annotation(text="mock_width_annot")]

        zone_data_row = self._create_minimal_load_zone_data_row(d_widths=[2.0] * num_d_points)
        load_zones_data = [zone_data_row]

        styling = self._get_default_styling_defaults()
        presentation = self._get_default_presentation_details()

        fig = build_load_zones_figure(load_zones_data, bridge_geom, styling, presentation)

        self.assertIsInstance(fig, go.Figure)

        # Check calls to mocks
        mock_calculate_bottom_y.assert_called_once()
        mock_get_appearance.assert_called_once()
        mock_create_fill_trace.assert_called_once()
        mock_create_boundary_lines.assert_called_once()
        mock_create_main_label.assert_called_once()
        mock_create_width_annots.assert_called_once()

        # Check figure content based on mocks
        self.assertEqual(len(fig.data), 2)  # fill + boundary
        self.assertIn(mock_create_fill_trace.return_value, fig.data)
        self.assertIn(mock_create_boundary_lines.return_value[0], fig.data)

        self.assertEqual(len(fig.layout.annotations), 2)  # main label + width annot
        self.assertIn(mock_create_main_label.return_value, fig.layout.annotations)
        self.assertIn(mock_create_width_annots.return_value[0], fig.layout.annotations)

        # Check layout
        self.assertEqual(fig.layout.title.text, presentation["figure_title"])
        # ... other layout checks as needed

    @patch("src.geometry.load_zone_plot.calculate_zone_bottom_y_coords")
    @patch("src.geometry.load_zone_plot.get_zone_appearance_properties")
    @patch("src.geometry.load_zone_plot.create_zone_fill_trace")
    @patch("src.geometry.load_zone_plot.create_zone_boundary_line_traces")
    @patch("src.geometry.load_zone_plot.create_zone_main_label_annotation")
    @patch("src.geometry.load_zone_plot.create_zone_width_annotations")
    def test_build_load_zones_figure_multiple_zones(
        self,
        mock_create_width_annots,
        mock_create_main_label,
        mock_create_boundary_lines,
        mock_create_fill_trace,
        mock_get_appearance,
        mock_calculate_bottom_y,
    ):
        """Test with multiple load zones."""
        num_d_points = 2
        bridge_geom = self._get_default_bridge_base_geometry(num_d_points=num_d_points)

        # Simulate y_coords changing for each zone. Each element of the tuple is list[float]
        mock_calculate_bottom_y.side_effect = [
            [3.0] * num_d_points,  # Zone 1 Bottom: list[float]
            [1.0] * num_d_points,  # Zone 2 Bottom: list[float]
        ]
        mock_get_appearance.return_value = {"line_color": "gray", "fill_color": "lightgray"}
        mock_create_fill_trace.return_value = go.Scatter(name="mock_fill")
        mock_create_boundary_lines.return_value = [go.Scatter(name="mock_boundary")]
        mock_create_main_label.return_value = go.layout.Annotation(text="mock_label")
        mock_create_width_annots.return_value = [go.layout.Annotation(text="mock_width")]

        zone1_data = self._create_minimal_load_zone_data_row(zone_type="TypeA", d_widths=[2.0] * num_d_points)
        zone2_data = self._create_minimal_load_zone_data_row(zone_type="TypeB", d_widths=[2.0] * num_d_points)
        load_zones_data = [zone1_data, zone2_data]

        styling = self._get_default_styling_defaults()
        presentation = self._get_default_presentation_details()

        fig = build_load_zones_figure(load_zones_data, bridge_geom, styling, presentation)

        self.assertEqual(mock_calculate_bottom_y.call_count, 2)
        self.assertEqual(mock_get_appearance.call_count, 2)
        self.assertEqual(mock_create_fill_trace.call_count, 2)
        self.assertEqual(mock_create_boundary_lines.call_count, 2)
        self.assertEqual(mock_create_main_label.call_count, 2)
        self.assertEqual(mock_create_width_annots.call_count, 2)

        self.assertEqual(len(fig.data), 4)  # 2 zones * (1 fill + 1 boundary)
        self.assertEqual(len(fig.layout.annotations), 4)  # 2 zones * (1 label + 1 width)

    @patch("src.geometry.load_zone_plot.calculate_zone_bottom_y_coords")
    @patch("src.geometry.load_zone_plot.get_zone_appearance_properties")
    @patch("src.geometry.load_zone_plot.create_zone_fill_trace")
    @patch("src.geometry.load_zone_plot.create_zone_boundary_line_traces")
    @patch("src.geometry.load_zone_plot.create_zone_main_label_annotation")
    @patch("src.geometry.load_zone_plot.create_zone_width_annotations")
    def test_build_load_zones_figure_with_validation_and_base_traces(
        self,
        mock_create_width_annots,
        mock_create_main_label,
        mock_create_boundary_lines,
        mock_create_fill_trace,
        mock_get_appearance,
        mock_calculate_bottom_y,
    ):
        """Test with validation messages and base traces."""
        num_d_points = 1
        bridge_geom = self._get_default_bridge_base_geometry(num_d_points=num_d_points)

        mock_calculate_bottom_y.return_value = [0.0] * num_d_points  # y_bottom as list[float]
        mock_get_appearance.return_value = {"line_color": "blue", "fill_color": "lightblue", "pattern_shape": ""}
        mock_create_fill_trace.return_value = go.Scatter(name="fill")
        mock_create_boundary_lines.return_value = [go.Scatter(name="boundary")]
        mock_create_main_label.return_value = go.layout.Annotation(text="label")
        mock_create_width_annots.return_value = [go.layout.Annotation(text="width")]

        load_zones_data = [self._create_minimal_load_zone_data_row(d_widths=[1.0] * num_d_points)]
        styling = self._get_default_styling_defaults()

        base_trace1 = go.Scatter(x=[0], y=[0], name="base1")
        validation_msg = ["Warning!"]
        presentation = PlotPresentationDetails(
            base_traces=[base_trace1],
            validation_messages=validation_msg,
            figure_title="Test With Extras",
        )

        fig = build_load_zones_figure(load_zones_data, bridge_geom, styling, presentation)

        self.assertIn(base_trace1, fig.data)
        self.assertEqual(len(fig.data), 3)  # 1 base + 1 fill + 1 boundary

        self.assertEqual(len(fig.layout.annotations), 3)  # label, width, validation
        validation_annotation = next(ann for ann in fig.layout.annotations if "Waarschuwing:" in ann.text)
        self.assertIsNotNone(validation_annotation)
        self.assertIn(validation_msg[0], validation_annotation.text)
        self.assertEqual(fig.layout.margin.b, 150)  # Check margin update due to validation message


if __name__ == "__main__":
    unittest.main()
