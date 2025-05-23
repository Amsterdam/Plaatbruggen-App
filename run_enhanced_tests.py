#!/usr/bin/env python3
"""
Enhanced test runner with colorful output and detailed failure reporting.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_utils import EnhancedTestResult, colored_text, Colors, safe_emoji_text


def main():
    """Run all tests with enhanced reporting."""
    print(colored_text(safe_emoji_text("🚀 STARTING ENHANCED TEST SUITE! 🚀", "STARTING ENHANCED TEST SUITE!"), Colors.BLUE, bold=True))
    print(colored_text("=" * 60, Colors.BLUE))
    
    # Discover all tests
    loader = unittest.TestLoader()
    test_suite = loader.discover('tests', pattern='test_*.py')
    
    # Create enhanced test runner
    runner = unittest.TextTestRunner(
        resultclass=EnhancedTestResult,
        verbosity=0,
        stream=sys.stdout
    )
    
    # Run tests
    result = runner.run(test_suite)
    
    # Final summary
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
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main() 