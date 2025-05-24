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
    passed = total_tests - failures - errors

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
        print(f"Ran {total_tests} tests: {passed} passed, {failures} failed, {errors} errors")  # noqa: T201

        # Show failed test details concisely
        if hasattr(result, "_concise_failures") and result._concise_failures:  # noqa: SLF001
            for failure in result._concise_failures:  # noqa: SLF001
                status = "ERROR" if failure["is_error"] else "FAIL"
                print(f"  {status}: {failure['test_class']}.{failure['test_name']}")  # noqa: T201
                print(f"    {failure['error_msg']}")  # noqa: T201

        # Overall status message
        print("\n" + "=" * 60)  # noqa: T201
        safe_emoji_text("❌ CHECKS FAILED! Fix issues before pushing!", "CHECKS FAILED! Fix issues before pushing!")
        print("=" * 60)  # noqa: T201


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
    # Force concise mode for pre-commit by detecting if we're running in a subprocess
    # This is a fallback in case our environment detection doesn't work
    is_subprocess = os.environ.get("_") != sys.executable
    concise_mode = is_subprocess or should_use_concise_mode()

    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

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
