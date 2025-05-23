"""Tests for VIKTOR views in app.bridge.controller module."""

import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from app.bridge.controller import BridgeController
from tests.test_data.seed_loader import load_bridge_complex_params, load_bridge_default_params
from tests.test_utils import view_test_wrapper


class TestBridgeControllerViews(unittest.TestCase):
    """Test cases for BridgeController VIKTOR views."""

    def setUp(self):
        """Set up test fixtures."""
        self.controller = BridgeController()
        self.default_params = load_bridge_default_params()
        self.complex_params = load_bridge_complex_params()

    def test_view_methods_exist(self):
        """Test that all view methods exist and are callable."""
        view_methods = [
            "get_3d_view",
            "get_bridge_summary_view",
            "get_2d_cross_section",
            "get_2d_horizontal_section",
            "get_2d_longitudinal_section",
            "get_top_view",
            "get_load_zones_view",
            "get_output_report",
            "get_bridge_map_view",
        ]

        for method_name in view_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(self.controller, method_name))
                self.assertTrue(callable(getattr(self.controller, method_name)))

    def test_controller_has_parametrization(self):
        """Test that the controller has the correct parametrization."""
        from app.bridge.parametrization import BridgeParametrization

        self.assertEqual(self.controller.parametrization, BridgeParametrization)

    def test_controller_label(self):
        """Test that the controller has the correct label."""
        self.assertEqual(self.controller.label, "Brug")

    # ============================================================================================================
    # PHASE 2: Full View Execution Tests - Bypassing VIKTOR Decorators
    # ============================================================================================================

    @view_test_wrapper("get_bridge_summary_view")
    def test_get_bridge_summary_view_execution(self):
        """Test actual execution of get_bridge_summary_view by calling the underlying method."""
        # Access the original method by getting the function from the class
        # The VIKTOR decorator wraps the method, so we need to access __wrapped__ or the original
        original_method = self.controller.__class__.get_bridge_summary_view

        # Call the method directly, bypassing the decorator
        result = original_method(self.controller, self.default_params)

        # Assert - verify return type and structure
        from viktor.views import DataResult

        self.assertIsInstance(result, DataResult)
        self.assertIsNotNone(result.data)

        # Verify specific data items are present
        # DataGroup extends dict, so DataItems are stored as values
        data_items = list(result.data.values())
        self.assertTrue(len(data_items) > 0)

        # Check for expected labels (DataItem uses _label attribute)
        labels = [item._label for item in data_items]
        expected_labels = ["Bridge ID (OBJECTNUMM)", "Bridge Name", "Location Description"]
        for expected_label in expected_labels:
            self.assertIn(expected_label, labels)

    @patch("app.bridge.controller.create_3d_model")
    @patch("trimesh.exchange.gltf.export_glb")
    @view_test_wrapper("get_3d_view")
    def test_get_3d_view_execution(self, mock_export_glb, mock_create_3d):
        """Test actual execution of get_3d_view with mocked dependencies."""
        # Arrange
        mock_scene = MagicMock()
        mock_create_3d.return_value = mock_scene
        mock_export_glb.return_value = b"fake_gltf_data"

        # Access the original method directly
        original_method = self.controller.__class__.get_3d_view

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import GeometryResult

        self.assertIsInstance(result, GeometryResult)
        mock_create_3d.assert_called_once_with(self.default_params, section_planes=True)
        mock_export_glb.assert_called_once_with(mock_scene)

    @patch("app.bridge.controller.build_top_view_figure")
    @patch("app.bridge.controller.create_2d_top_view")
    @patch("app.bridge.controller.validate_load_zone_widths")
    @view_test_wrapper("get_top_view")
    def test_get_top_view_execution(self, mock_validate_widths, mock_create_2d, mock_build_figure):
        """Test actual execution of get_top_view with mocked dependencies."""
        # Arrange
        mock_top_view_data = {"bridge_lines": [], "structural_polygons": []}
        mock_create_2d.return_value = mock_top_view_data
        mock_validate_widths.return_value = []

        mock_fig = Mock()
        mock_fig.to_json.return_value = '{"data": [], "layout": {}}'
        mock_build_figure.return_value = mock_fig

        # Access the original method directly
        original_method = self.controller.__class__.get_top_view

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)
        mock_create_2d.assert_called_once_with(self.default_params)
        mock_build_figure.assert_called_once()

        # Verify JSON result is valid - PlotlyResult stores figure in .figure attribute
        json_result = json.loads(result.figure)
        self.assertIn("data", json_result)
        self.assertIn("layout", json_result)

    @patch("app.bridge.controller.create_horizontal_section_view")
    @view_test_wrapper("get_2d_horizontal_section")
    def test_get_2d_horizontal_section_execution(self, mock_create_horizontal):
        """Test actual execution of get_2d_horizontal_section."""
        # Arrange
        mock_fig = Mock()
        mock_fig.to_json.return_value = '{"data": [], "layout": {"title": "Horizontal Section"}}'
        mock_create_horizontal.return_value = mock_fig

        # Access the original method directly
        original_method = self.controller.__class__.get_2d_horizontal_section

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)
        mock_create_horizontal.assert_called_once_with(self.default_params, self.default_params.input.dimensions.horizontal_section_loc)

        # Verify JSON result - PlotlyResult stores figure in .figure attribute
        json_result = json.loads(result.figure)
        self.assertIn("layout", json_result)

    @patch("app.bridge.controller.create_longitudinal_section")
    @view_test_wrapper("get_2d_longitudinal_section")
    def test_get_2d_longitudinal_section_execution(self, mock_create_longitudinal):
        """Test actual execution of get_2d_longitudinal_section."""
        # Arrange
        mock_fig = Mock()
        mock_fig.to_json.return_value = '{"data": [], "layout": {"title": "Longitudinal Section"}}'
        mock_create_longitudinal.return_value = mock_fig

        # Access the original method directly
        original_method = self.controller.__class__.get_2d_longitudinal_section

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)
        mock_create_longitudinal.assert_called_once_with(self.default_params, self.default_params.input.dimensions.longitudinal_section_loc)

    @patch("app.bridge.controller.create_cross_section_view")
    @view_test_wrapper("get_2d_cross_section")
    def test_get_2d_cross_section_execution(self, mock_create_cross):
        """Test actual execution of get_2d_cross_section."""
        # Arrange
        mock_fig = Mock()
        mock_fig.to_json.return_value = '{"data": [], "layout": {"title": "Cross Section"}}'
        mock_create_cross.return_value = mock_fig

        # Access the original method directly
        original_method = self.controller.__class__.get_2d_cross_section

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)
        mock_create_cross.assert_called_once_with(self.default_params, self.default_params.input.dimensions.cross_section_loc)

    @patch("app.bridge.controller.build_load_zones_figure")
    @view_test_wrapper("get_load_zones_view")
    def test_get_load_zones_view_execution_with_zones(self, mock_build_zones):
        """Test actual execution of get_load_zones_view with load zones present."""
        # Arrange
        mock_fig = Mock()
        mock_fig.to_json.return_value = '{"data": [], "layout": {"title": "Load Zones"}}'
        mock_build_zones.return_value = mock_fig

        # Access the original method directly
        original_method = self.controller.__class__.get_load_zones_view

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)

        # Verify JSON result
        json_result = json.loads(result.figure)
        self.assertIn("data", json_result)
        self.assertIn("layout", json_result)

    @view_test_wrapper("get_load_zones_view")
    def test_get_load_zones_view_no_zones(self):
        """Test get_load_zones_view when no load zones are defined."""
        # Arrange - create params with empty load zones
        params_no_zones = self.default_params.copy()
        params_no_zones.load_zones_data_array = []

        # Access the original method directly
        original_method = self.controller.__class__.get_load_zones_view

        # Act - call bypassing decorator
        result = original_method(self.controller, params_no_zones)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)

        # Should return a figure with appropriate message
        json_result = json.loads(result.figure)
        self.assertIn("layout", json_result)

    @patch("app.bridge.controller.api_sdk.API")
    @view_test_wrapper("get_bridge_map_view")
    def test_get_bridge_map_view_execution_invalid_entity(self, mock_api_class):
        """Test get_bridge_map_view with invalid entity ID."""
        # Access the original method directly
        original_method = self.controller.__class__.get_bridge_map_view

        # Act - call bypassing decorator with entity_id in kwargs
        result = original_method(self.controller, self.default_params, entity_id=None)

        # Assert
        from viktor.views import MapResult

        self.assertIsInstance(result, MapResult)
        self.assertTrue(len(result.features) > 0)

        # Should contain error message
        error_point = result.features[0]
        self.assertIn("Ongeldige entity ID", error_point._description)

    @patch("app.bridge.controller.convert_word_to_pdf")
    @view_test_wrapper("get_output_report")
    def test_get_output_report_execution(self, mock_convert_pdf):
        """Test actual execution of get_output_report."""
        # Arrange
        mock_pdf_file = Mock()
        mock_convert_pdf.return_value = mock_pdf_file

        # Access the original method directly
        original_method = self.controller.__class__.get_output_report

        # Act - call bypassing decorator
        result = original_method(self.controller, self.default_params)

        # Assert
        from viktor.views import PDFResult

        self.assertIsInstance(result, PDFResult)
        mock_convert_pdf.assert_called_once()

    # ============================================================================================================
    # Error Handling Tests
    # ============================================================================================================

    @patch("app.bridge.controller.create_3d_model")
    @view_test_wrapper("get_3d_view")
    def test_get_3d_view_error_handling(self, mock_create_3d):
        """Test error handling in get_3d_view when 3D model creation fails."""
        # Arrange
        mock_create_3d.side_effect = Exception("3D model creation failed")

        # Access the original method directly
        original_method = self.controller.__class__.get_3d_view

        # Act & Assert
        with self.assertRaises(Exception):
            original_method(self.controller, self.default_params)

    @view_test_wrapper("get_load_zones_view")
    def test_get_load_zones_view_invalid_bridge_segments(self):
        """Test get_load_zones_view when bridge segments are invalid."""
        # Arrange - create params with invalid bridge segments
        params_invalid = self.default_params.copy()
        params_invalid.bridge_segments_array = []  # Empty segments

        # Access the original method directly
        original_method = self.controller.__class__.get_load_zones_view

        # Act - call bypassing decorator
        result = original_method(self.controller, params_invalid)

        # Assert
        from viktor.views import PlotlyResult

        self.assertIsInstance(result, PlotlyResult)

        # Should return error figure
        json_result = json.loads(result.figure)
        self.assertIn("layout", json_result)

    # ============================================================================================================
    # Data Validation Tests
    # ============================================================================================================

    def test_seed_data_loaded_correctly(self):
        """Test that seed data is loaded correctly for view testing."""
        # Test default params
        self.assertIn("info", self.default_params)
        self.assertIn("bridge_segments_array", self.default_params)
        self.assertIn("load_zones_data_array", self.default_params)

        # Test complex params
        self.assertIn("info", self.complex_params)
        self.assertIn("bridge_segments_array", self.complex_params)
        self.assertIn("load_zones_data_array", self.complex_params)

        # Verify structure for view method access
        self.assertTrue(hasattr(self.default_params.info, "bridge_objectnumm"))
        self.assertTrue(hasattr(self.default_params.info, "bridge_name"))
        self.assertTrue(hasattr(self.default_params.input.dimensions, "horizontal_section_loc"))

    @view_test_wrapper("get_bridge_summary_view")
    def test_bridge_summary_view_with_complex_data(self):
        """Test bridge summary view with complex seed data."""
        # Access the original method directly
        original_method = self.controller.__class__.get_bridge_summary_view

        # Act - call bypassing decorator
        result = original_method(self.controller, self.complex_params)

        # Assert
        from viktor.views import DataResult

        self.assertIsInstance(result, DataResult)

        # Verify data items contain complex data values
        # DataGroup extends dict, so DataItems are stored as values
        data_items = list(result.data.values())
        bridge_id_item = next((item for item in data_items if item._label == "Bridge ID (OBJECTNUMM)"), None)
        self.assertIsNotNone(bridge_id_item)
        self.assertEqual(bridge_id_item._value, "BRIDGE-COMPLEX-001")


if __name__ == "__main__":
    unittest.main()
