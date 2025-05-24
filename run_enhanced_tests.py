#!/usr/bin/env python3
"""Enhanced test runner with colorful output and detailed failure reporting."""

import os
import sys
import unittest
from pathlib import Path
from unittest import TextTestResult

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_utils import EnhancedTestResult, safe_emoji_text, should_use_concise_mode  # noqa: E402


def print_concise_summary(result: TextTestResult) -> None:
    """Print a concise summary for git hooks."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)

    # Always show a summary line for git hooks
    if failures == 0 and errors == 0:
        safe_emoji_text("✅ ALL TESTS PASSED!", "ALL TESTS PASSED!")
        print(f"Ran {total_tests} tests successfully")  # noqa: T201

        # Overall status message (appears at the end since tests run last)
        print("\n" + "=" * 60)  # noqa: T201
        safe_emoji_text("🎉 ALL CHECKS DONE! Safe to push! 🎉", "ALL CHECKS DONE! Safe to push!")
        print("=" * 60)  # noqa: T201
    else:
        safe_emoji_text("❌ TESTS FAILED", "TESTS FAILED")
        print("Run 'python run_enhanced_tests.py' for detailed error information")  # noqa: T201

        # Show only first few failed test names concisely
        if hasattr(result, "_concise_failures") and result._concise_failures:  # noqa: SLF001
            failed_tests = result._concise_failures[:3]  # noqa: SLF001
            for failure in failed_tests:
                status = "ERROR" if failure["is_error"] else "FAIL"
                print(f"  {status}: {failure['test_class']}.{failure['test_name']}")  # noqa: T201
                print(f"    {failure['error_msg']}")  # noqa: T201

            if len(result._concise_failures) > 3:  # noqa: SLF001
                remaining = len(result._concise_failures) - 3  # noqa: SLF001
                print(f"  ... and {remaining} more test failures")  # noqa: T201

        # Don't show final "CHECKS FAILED" message here - let the hook system handle overall status


def print_detailed_summary(result: TextTestResult) -> None:
    """Print detailed summary for manual runs."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors

    if failures == 0 and errors == 0:
        safe_emoji_text("🎉 ALL TESTS PASSED! 🎉", "ALL TESTS PASSED!")
        print(f"Successfully ran {total_tests} tests")  # noqa: T201
    else:
        safe_emoji_text("❌ SOME TESTS FAILED", "SOME TESTS FAILED")
        print(f"Test results: {passed} passed, {failures} failed, {errors} errors out of {total_tests} total")  # noqa: T201


def main() -> None:
    """Run all tests with enhanced reporting."""
    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

    # Use the improved environment detection from test_utils
    concise_mode = should_use_concise_mode()

    # In concise mode, don't show startup message
    if not concise_mode:
        print("Running enhanced test suite...")  # noqa: T201
        print("=" * 60)  # noqa: T201

    # Discover all tests
    loader = unittest.TestLoader()
    test_suite = loader.discover("tests", pattern="test_*.py")

    # Create enhanced test runner with minimal output in concise mode
    verbosity = 0  # Always use minimal verbosity for both modes
    runner = unittest.TextTestRunner(resultclass=EnhancedTestResult, verbosity=verbosity, stream=sys.stdout)

    # Run tests
    result = runner.run(test_suite)

    # Print appropriate summary
    if concise_mode:
        print_concise_summary(result)
    else:
        print_detailed_summary(result)

    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
