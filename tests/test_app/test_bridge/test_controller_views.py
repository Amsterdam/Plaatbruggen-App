"""Tests for VIKTOR views in app.bridge.controller module."""

import unittest
from munch import Munch  # type: ignore[import-untyped]

from app.bridge.controller import BridgeController
from tests.test_data.seed_loader import load_bridge_default_params, load_bridge_complex_params
from tests.test_utils import view_test_wrapper, colored_text, Colors


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
            'get_3d_view',
            'get_bridge_summary_view',
            'get_2d_cross_section',
            'get_2d_horizontal_section',
            'get_2d_longitudinal_section',
            'get_top_view',
            'get_load_zones_view',
            'get_output_report',
            'get_bridge_map_view'
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

    def test_seed_data_loaded_correctly(self):
        """Test that seed data is loaded correctly."""
        # Test default params
        self.assertIn("info", self.default_params)
        self.assertIn("bridge_segments_array", self.default_params)
        
        # Test complex params
        self.assertIn("info", self.complex_params)
        self.assertIn("bridge_segments_array", self.complex_params)


if __name__ == '__main__':
    unittest.main() 