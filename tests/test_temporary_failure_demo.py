"""Temporary test file to demonstrate failing test output formatting."""

import unittest


class TestTemporaryFailureDemo(unittest.TestCase):
    """Temporary test class to show failure output."""

    def test_deliberate_assertion_failure(self) -> None:
        """Test that deliberately fails with assertion error."""
        # This will fail to show assertion error formatting
        assert 1 == 2, "This is a deliberate failure to test output formatting"

    def test_deliberate_exception_error(self) -> None:
        """Test that deliberately raises an exception."""
        # This will raise an exception to show error formatting
        msg = "This is a deliberate exception to test error formatting"
        raise ValueError(msg)

    def test_deliberate_type_error(self) -> None:
        """Test that deliberately causes a type error."""
        # This will cause a type error to show different error formatting
        result = "string" + 42  # noqa: F841


if __name__ == "__main__":
    unittest.main()
