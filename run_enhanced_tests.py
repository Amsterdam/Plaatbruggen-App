#!/usr/bin/env python3
"""
Enhanced test runner with colorful output and detailed failure reporting.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_utils import Colors, EnhancedTestResult, colored_text, safe_emoji_text, should_use_concise_mode


def print_concise_summary(result):
    """Print a concise summary for git hooks."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors

    # Always show a summary line for git hooks
    if failures == 0 and errors == 0:
        success_msg = safe_emoji_text("✅ ALL TESTS PASSED!", "ALL TESTS PASSED!")
        print(colored_text(success_msg, Colors.GREEN, bold=True))
        count_msg = f"Tests: {total_tests} passed"
        print(colored_text(count_msg, Colors.GREEN))
        print(colored_text("All tests passed, ready to push!", Colors.GREEN, bold=True))
    else:
        fail_msg = safe_emoji_text("❌ TESTS FAILED", "TESTS FAILED")
        print(colored_text(fail_msg, Colors.RED, bold=True))
        count_msg = f"Tests: {failures} failed, {errors} errors, {successes} passed, {total_tests} total"
        print(colored_text(count_msg, Colors.WHITE))

        # Show failed test details concisely
        if hasattr(result, "_concise_failures") and result._concise_failures:
            fail_header = "\nFailed tests:"
            print(colored_text(fail_header, Colors.YELLOW, bold=True))
            for failure in result._concise_failures:
                status = "ERROR" if failure["is_error"] else "FAIL"
                test_line = f"  {status}: {failure['test_class']}.{failure['test_name']}"
                print(colored_text(test_line, Colors.RED))
                error_line = f"    {failure['error_msg']}"
                print(colored_text(error_line, Colors.WHITE))

        help_header = "\nFor detailed output, run:"
        print(colored_text(help_header, Colors.CYAN))
        help_cmd = "  python run_enhanced_tests.py"
        print(colored_text(help_cmd, Colors.WHITE))
        print(colored_text("Tests failed, please fix before pushing!", Colors.RED, bold=True))


def print_detailed_summary(result):
    """Print detailed summary for manual runs."""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors

    print("\n" + colored_text(safe_emoji_text("🎯 TEST SUMMARY", "TEST SUMMARY"), Colors.BLUE, bold=True))
    print(colored_text(safe_emoji_text(f"✅ Successes: {successes}", f"Successes: {successes}"), Colors.GREEN))
    print(colored_text(safe_emoji_text(f"❌ Failures: {failures}", f"Failures: {failures}"), Colors.YELLOW))
    print(colored_text(safe_emoji_text(f"💥 Errors: {errors}", f"Errors: {errors}"), Colors.RED))
    print(colored_text(safe_emoji_text(f"📊 Total: {total_tests}", f"Total: {total_tests}"), Colors.CYAN))

    if failures == 0 and errors == 0:
        print(colored_text(safe_emoji_text("🎉 ALL TESTS PASSED! 🎉", "ALL TESTS PASSED!"), Colors.GREEN, bold=True))
    else:
        print(colored_text(safe_emoji_text("🔥 SOME TESTS FAILED! TIME TO DEBUG! 🔥", "SOME TESTS FAILED! TIME TO DEBUG!"), Colors.RED, bold=True))


def main():
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
        print(colored_text(safe_emoji_text("🚀 STARTING ENHANCED TEST SUITE! 🚀", "STARTING ENHANCED TEST SUITE!"), Colors.BLUE, bold=True))
        print(colored_text("=" * 60, Colors.BLUE))

    # Discover all tests
    loader = unittest.TestLoader()
    test_suite = loader.discover("tests", pattern="test_*.py")

    # Create enhanced test runner with minimal output in concise mode
    verbosity = 0 if concise_mode else 0
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
