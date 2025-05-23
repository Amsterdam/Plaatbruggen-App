"""
Demo test file with intentional failures to test enhanced error reporting.
"""

import unittest


class TestDemoFailures(unittest.TestCase):
    """Demo test class with intentional failures."""

    def test_simple_assertion_failure(self) -> None:
        """Test that demonstrates a simple assertion failure."""
        expected_value = 42
        actual_value = 24
        self.assertEqual(expected_value, actual_value, "Expected and actual values should match")

    def test_error_with_exception(self) -> None:
        """Test that demonstrates an error with exception."""
        # This will raise a ZeroDivisionError
        result = 10 / 0  # noqa: F841

    def test_string_comparison_failure(self) -> None:
        """Test that demonstrates string comparison failure."""
        expected_text = "Hello, World!"
        actual_text = "Hello, Universe!"
        self.assertEqual(expected_text, actual_text, "Greeting texts should match")


if __name__ == "__main__":
    unittest.main() 