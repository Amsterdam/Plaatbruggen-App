"""
Temporary test file to test failure output during git push.
DELETE THIS FILE AFTER TESTING.
"""

import unittest


class TestTempFailure(unittest.TestCase):
    """Temporary test to see failure output in git hooks."""

    def test_intentional_failure(self):
        """This test will fail to show git hook output."""
        self.assertEqual(42, 24, "This should fail to test git hook output!")

    def test_success(self):
        """This test should pass."""
        self.assertEqual(2 + 2, 4)


if __name__ == "__main__":
    unittest.main() 