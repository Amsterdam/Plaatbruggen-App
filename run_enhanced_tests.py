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

from tests.test_utils import (  # noqa: E402
    Colors,
    EnhancedTestResult,
    colored_text,
    colorized_status_message,
    safe_arrow,
    safe_emoji_text,
    should_use_concise_mode,
)


def print_concise_summary(result: TextTestResult, warning_mode: bool = False) -> None:
    """Print a concise summary for git hooks."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)

    # Always show a summary line for git hooks
    if failures == 0 and errors == 0:
        safe_emoji_text("✅ ALL TESTS PASSED!", "ALL TESTS PASSED!")
        print(colorized_status_message(f"Ran {total_tests} tests successfully", is_success=True))  # noqa: T201

        # Overall status message - more generic since other checks might have failed
        print("\n" + "=" * 60)  # noqa: T201
        print(colorized_status_message("ALL CHECKS COMPLETED", is_success=False, is_warning=True))  # noqa: T201
        print(  # noqa: T201
            colorized_status_message("Check the logs above. If there are no errors, your changes will be pushed.", is_success=False, is_warning=True)
        )
        print("=" * 60)  # noqa: T201
    else:
        if warning_mode:
            safe_emoji_text("⚠️ TESTS FAILED", "TESTS FAILED")
            print(colorized_status_message(f"Test failures found: {failures + errors} issues", is_success=False, is_warning=True))  # noqa: T201
            print(colorized_status_message("⚠️ WARNING: This PR cannot be merged until test failures are fixed!", is_success=False, is_warning=True))  # noqa: T201
            print(colorized_status_message("Run the following command to fix issues:", is_success=False, is_warning=True))  # noqa: T201
        else:
            safe_emoji_text("❌ TESTS FAILED", "TESTS FAILED")
            print(colorized_status_message("Run the following command for detailed test error information:", is_success=False, is_warning=True))  # noqa: T201
        print(f"  {safe_arrow()}{colored_text('python run_enhanced_tests.py', Colors.CYAN, bold=True)}")  # noqa: T201

        # Don't show final "CHECKS FAILED" message here - let the hook system handle overall status


def print_detailed_summary(result: TextTestResult) -> None:
    """Print detailed summary for manual runs."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors

    if failures == 0 and errors == 0:
        safe_emoji_text("🎉 ALL TESTS PASSED! 🎉", "ALL TESTS PASSED!")
        print(colorized_status_message(f"Successfully ran {total_tests} tests", is_success=True))  # noqa: T201
    else:
        safe_emoji_text("❌ SOME TESTS FAILED", "SOME TESTS FAILED")
        print(  # noqa: T201
            colorized_status_message(
                f"Test results: {passed} passed, {failures} failed, {errors} errors out of {total_tests} total", is_success=False
            )
        )

        print("\n" + "=" * 60)  # noqa: T201
        print(colorized_status_message("DETAILED ERROR INFORMATION:", is_success=False))  # noqa: T201
        print("=" * 60)  # noqa: T201

        # Show detailed failures
        if result.failures:
            print(colorized_status_message(f"\nFAILURES ({len(result.failures)}):", is_success=False))  # noqa: T201
            for i, (test, traceback) in enumerate(result.failures, 1):
                test_name = f"{test.__class__.__name__}.{test._testMethodName}"  # noqa: SLF001
                print(f"\n{i}. {colorized_status_message(test_name, is_success=False)}")  # noqa: T201
                print(traceback)  # noqa: T201

        # Show detailed errors
        if result.errors:
            print(colorized_status_message(f"\nERRORS ({len(result.errors)}):", is_success=False))  # noqa: T201
            for i, (test, traceback) in enumerate(result.errors, 1):
                test_name = f"{test.__class__.__name__}.{test._testMethodName}"  # noqa: SLF001
                print(f"\n{i}. {colorized_status_message(test_name, is_success=False)}")  # noqa: T201
                print(traceback)  # noqa: T201

        print("\n" + "=" * 60)  # noqa: T201
        print(colorized_status_message("TIP: Focus on fixing errors first, then failures", is_success=False, is_warning=True))  # noqa: T201
        print("=" * 60)  # noqa: T201


def main() -> None:
    """Run all tests with enhanced reporting."""
    # Check for warning mode
    warning_mode = "--warning-mode" in sys.argv
    
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
    runner = unittest.TextTestRunner(resultclass=EnhancedTestResult, verbosity=verbosity, stream=sys.stdout)  # type: ignore[arg-type]

    # Run tests
    result = runner.run(test_suite)

    # Print appropriate summary
    if concise_mode:
        print_concise_summary(result, warning_mode)
    else:
        print_detailed_summary(result)

    # Exit with appropriate code
    if warning_mode:
        # In warning mode, always exit with 0 to allow push to continue
        sys.exit(0)
    elif result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
