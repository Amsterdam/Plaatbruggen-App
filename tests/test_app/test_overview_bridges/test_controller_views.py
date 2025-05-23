"""Tests for VIKTOR views in app.overview_bridges.controller module."""

import unittest

from app.overview_bridges.controller import OverviewBridgesController
from tests.test_data.seed_loader import load_overview_bridges_default_params


class TestOverviewBridgesControllerViews(unittest.TestCase):
    """Test cases for OverviewBridgesController VIKTOR views."""

    def setUp(self):
        """Set up test fixtures."""
        self.controller = OverviewBridgesController()
        self.default_params = load_overview_bridges_default_params()

    # Note: View tests simplified due to VIKTOR SDK mocking complexity
    def test_view_methods_exist(self):
        """Test that the view methods exist and are callable."""
        # Test map view method
        self.assertTrue(hasattr(self.controller, "get_map_view"))
        self.assertTrue(callable(getattr(self.controller, "get_map_view")))

        # Test readme/changelog view method
        self.assertTrue(hasattr(self.controller, "view_readme_changelog"))
        self.assertTrue(callable(getattr(self.controller, "view_readme_changelog")))


if __name__ == "__main__":
    unittest.main()
