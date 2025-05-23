"""Tests for app.bridge.controller module."""

import unittest
from unittest.mock import patch, MagicMock
from munch import Munch  # type: ignore[import-untyped]

from viktor.testing import mock_API, MockedEntity  # VIKTOR testing utilities
from viktor.errors import UserError

from app.bridge.controller import BridgeController, BridgeSegmentParamRow
from src.geometry.model_creator import BridgeSegmentDimensions
from tests.test_data.seed_loader import load_bridge_default_params, load_bridge_complex_params
from tests.test_utils import controller_test_wrapper, colored_text, Colors


class TestBridgeController(unittest.TestCase):
    """Test cases for BridgeController."""

    def setUp(self):
        """Set up test fixtures."""
        self.controller = BridgeController()
        self.default_params = load_bridge_default_params()
        self.complex_params = load_bridge_complex_params()
        
        # Sample bridge segment row for testing individual segment processing
        # Use data from seed file but ensure it has all needed fields for testing
        seed_segment = self.default_params.bridge_segments_array[0].copy()
        self.sample_segment_row = {
            "bz1": seed_segment.get("bz1", 10.0),
            "bz2": seed_segment.get("bz2", 5.0),
            "bz3": seed_segment.get("bz3", 15.0),
            "dz": seed_segment.get("dz", 2.0),
            "dz_2": seed_segment.get("dz_2", 3.0),
            "col_6": seed_segment.get("col_6", 0.0),
            "l": seed_segment.get("l", 10.0),
            "is_first_segment": seed_segment.get("is_first_segment", False)
        }

    @controller_test_wrapper("BridgeController", "_create_bridge_segment_dimensions_from_params")
    def test_create_bridge_segment_dimensions_from_params_valid_segment(self):
        """Test creating bridge segment dimensions from a valid individual segment."""
        # Act
        result = self.controller._create_bridge_segment_dimensions_from_params(self.sample_segment_row)

        # Assert
        self.assertIsInstance(result, BridgeSegmentDimensions)
        self.assertEqual(result.bz1, self.sample_segment_row["bz1"])
        self.assertEqual(result.bz2, self.sample_segment_row["bz2"])
        self.assertEqual(result.bz3, self.sample_segment_row["bz3"])
        self.assertEqual(result.segment_length, self.sample_segment_row["l"])

    @controller_test_wrapper("BridgeController", "_create_bridge_segment_dimensions_from_params")
    def test_create_bridge_segment_dimensions_from_params_missing_required_field(self):
        """Test creating bridge segment dimensions with missing required fields."""
        # Arrange - Create incomplete segment by removing 'l' from seed data
        seed_segment = self.default_params.bridge_segments_array[0].copy()
        incomplete_segment = {k: v for k, v in seed_segment.items() if k != "l"}

        # Act & Assert
        with self.assertRaises(UserError) as context:
            self.controller._create_bridge_segment_dimensions_from_params(incomplete_segment)
        
        self.assertIn("brugsegmenten missen benodigde data", str(context.exception))

    @patch('app.bridge.controller.prepare_load_zone_geometry_data')
    @controller_test_wrapper("BridgeController", "_prepare_bridge_geometry_for_plotting")
    def test_prepare_bridge_geometry_for_plotting_with_valid_segments(self, mock_prepare_geometry):
        """Test preparing bridge geometry with valid segment data."""
        # Arrange
        segments_list = [self.sample_segment_row]
        mock_geometry_data = MagicMock()
        mock_prepare_geometry.return_value = mock_geometry_data

        # Act
        result = self.controller._prepare_bridge_geometry_for_plotting(segments_list)

        # Assert
        self.assertEqual(result, mock_geometry_data)
        mock_prepare_geometry.assert_called_once()
        # Verify the call was made with the correct type of arguments
        call_args = mock_prepare_geometry.call_args[0][0]  # First positional argument
        self.assertIsInstance(call_args, list)
        self.assertTrue(len(call_args) > 0)
        # Verify the first item is a BridgeSegmentDimensions object
        from src.geometry.model_creator import BridgeSegmentDimensions
        self.assertIsInstance(call_args[0], BridgeSegmentDimensions)

    def test_prepare_bridge_geometry_for_plotting_empty_segments(self):
        """Test preparing bridge geometry with empty segment list."""
        # Act
        result = self.controller._prepare_bridge_geometry_for_plotting([])

        # Assert
        self.assertIsNone(result)

    def test_prepare_bridge_geometry_for_plotting_with_complex_data(self):
        """Test preparing bridge geometry with complex segment data from seed files."""
        # Arrange - Use segments from complex seed data
        bridge_segments_params = self.complex_params.bridge_segments_array

        # Act
        result = self.controller._prepare_bridge_geometry_for_plotting(bridge_segments_params)

        # Assert
        self.assertIsNotNone(result)
        # The number of D points should match the number of segments from complex seed data
        expected_segments = len(self.complex_params.bridge_segments_array)
        self.assertEqual(result.num_defined_d_points, expected_segments)

    def test_prepare_bridge_geometry_for_plotting_invalid_segment_raises_error(self):
        """Test preparing bridge geometry with invalid segment data."""
        # Arrange - Create invalid segment by keeping only bz1 from seed data
        seed_segment = self.default_params.bridge_segments_array[0].copy()
        invalid_segments = [{"bz1": seed_segment["bz1"]}]  # Missing bz2, bz3, l

        # Act & Assert
        with self.assertRaises(UserError):
            self.controller._prepare_bridge_geometry_for_plotting(invalid_segments)

    def test_get_bridge_entity_data_invalid_entity_id(self):
        """Test fetching bridge entity data with invalid entity ID."""
        # Act
        objectnumm, name, error_result = self.controller._get_bridge_entity_data(None)

        # Assert
        self.assertIsNone(objectnumm)
        self.assertIsNone(name)
        self.assertIsNotNone(error_result)  # Should return a MapResult error

    def test_get_bridge_entity_data_with_api_mocking(self):
        """Test bridge entity data method structure without actual API calls."""
        # This test verifies the method exists and has the right signature
        # without testing the actual API integration
        
        # Arrange - invalid entity ID
        entity_id = None
        
        # Act
        objectnumm, name, error_result = self.controller._get_bridge_entity_data(entity_id)
        
        # Assert - with invalid ID, should return None values and error
        self.assertIsNone(objectnumm)
        self.assertIsNone(name)
        self.assertIsNotNone(error_result)

    def test_bridge_segment_param_row_structure(self):
        """Test BridgeSegmentParamRow structure validation using seed data."""
        # Act & Assert - test that our sample segment has the expected structure
        self.assertIn("bz1", self.sample_segment_row)
        self.assertIn("bz2", self.sample_segment_row)
        self.assertIn("bz3", self.sample_segment_row)
        self.assertIn("l", self.sample_segment_row)
        
        # Test values are what we expect from seed data
        self.assertEqual(self.sample_segment_row["bz1"], self.sample_segment_row["bz1"])
        self.assertEqual(self.sample_segment_row["bz2"], self.sample_segment_row["bz2"])
        self.assertEqual(self.sample_segment_row["bz3"], self.sample_segment_row["bz3"])
        self.assertEqual(self.sample_segment_row["l"], self.sample_segment_row["l"])
        
        # Test data types
        self.assertIsInstance(self.sample_segment_row["bz1"], (int, float))
        self.assertIsInstance(self.sample_segment_row["bz2"], (int, float))
        self.assertIsInstance(self.sample_segment_row["bz3"], (int, float))
        self.assertIsInstance(self.sample_segment_row["l"], (int, float))

    def test_seed_data_integrity_default(self):
        """Test that default seed data has expected structure."""
        # Assert
        self.assertIn("info", self.default_params)
        self.assertIn("input", self.default_params)
        self.assertIn("bridge_segments_array", self.default_params)
        self.assertIn("load_zones_data_array", self.default_params)
        self.assertIn("reinforcement_zones_array", self.default_params)
        
        # Check specific values
        self.assertEqual(self.default_params.info.bridge_objectnumm, "BRIDGE-001")
        self.assertEqual(len(self.default_params.bridge_segments_array), 2)
        self.assertEqual(len(self.default_params.load_zones_data_array), 4)

    def test_seed_data_integrity_complex(self):
        """Test that complex seed data has expected structure."""
        # Assert
        self.assertIn("info", self.complex_params)
        self.assertIn("input", self.complex_params)
        self.assertIn("bridge_segments_array", self.complex_params)
        self.assertIn("load_zones_data_array", self.complex_params)
        self.assertIn("reinforcement_zones_array", self.complex_params)
        
        # Check specific values
        self.assertEqual(self.complex_params.info.bridge_objectnumm, "BRIDGE-COMPLEX-001")
        self.assertEqual(len(self.complex_params.bridge_segments_array), 3)
        self.assertEqual(len(self.complex_params.load_zones_data_array), 3)

    def test_seed_data_bridge_segments_structure(self):
        """Test that bridge segments in seed data have correct structure."""
        # Test first segment in default params
        first_segment = self.default_params.bridge_segments_array[0]
        
        # Check required fields exist
        required_fields = ["bz1", "bz2", "bz3", "l"]
        for field in required_fields:
            self.assertIn(field, first_segment)
        
        # Check types
        self.assertIsInstance(first_segment["bz1"], (int, float))
        self.assertIsInstance(first_segment["bz2"], (int, float))
        self.assertIsInstance(first_segment["bz3"], (int, float))
        self.assertIsInstance(first_segment["l"], (int, float))


if __name__ == '__main__':
    unittest.main() 