"""
Test utilities for enhanced error reporting and colorful output.
"""

import functools
import os
import sys
import traceback
import unittest
from typing import Callable


def is_git_hook_environment() -> bool:
    """Detect if we're running in a git hook or CI environment where emojis might not work."""
    # Check for common git hook environment variables
    git_hook_indicators = ["GIT_DIR", "GIT_INDEX_FILE", "GIT_AUTHOR_NAME", "CI", "GITHUB_ACTIONS", "GITLAB_CI"]

    return any(os.environ.get(indicator) for indicator in git_hook_indicators)


class Colors:
    """ANSI color codes for terminal output."""

    # Basic colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Reset
    RESET = "\033[0m"

    @classmethod
    def disable_on_windows_if_needed(cls):
        """Disable colors on Windows if ANSI support is not available."""
        if sys.platform.startswith("win") or is_git_hook_environment():
            try:
                # Try to enable ANSI support on Windows 10+
                import os

                os.system("color")
            except:
                # Fallback: disable colors
                for attr in dir(cls):
                    if not attr.startswith("_") and attr != "disable_on_windows_if_needed":
                        setattr(cls, attr, "")


def colored_text(text: str, color: str, bold: bool = False) -> str:
    """Create colored text with optional bold styling."""
    # In git hooks, just return plain text
    if is_git_hook_environment():
        return text

    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"


def safe_emoji_text(emoji_text: str, plain_text: str) -> str:
    """Return emoji text if supported, otherwise plain text."""
    if is_git_hook_environment():
        return plain_text

    try:
        # Test if we can encode the emoji to the console's encoding
        console_encoding = sys.stdout.encoding or "utf-8"
        emoji_text.encode(console_encoding)

        # Additional check for Windows cp1252 which claims to support unicode but doesn't handle emojis well
        if console_encoding.lower() in ("cp1252", "windows-1252"):
            return plain_text

        return emoji_text
    except (UnicodeEncodeError, AttributeError, LookupError):
        return plain_text


def detailed_failure_message(test_name: str, view_name: str, function_name: str, error_details: str) -> str:
    """Create a detailed failure message with colors and formatting."""
    header = colored_text(safe_emoji_text("🔥 VIEW TEST FAILURE! 🔥", "VIEW TEST FAILURE!"), Colors.RED, bold=True)
    test_info = colored_text(f"Test: {test_name}", Colors.CYAN)
    view_info = colored_text(f"View: {view_name}", Colors.YELLOW)
    func_info = colored_text(f"Function: {function_name}", Colors.MAGENTA)
    error_header = colored_text(safe_emoji_text("💥 Error Details:", "Error Details:"), Colors.RED, bold=True)

    return f"""
{header}
{test_info}
{view_info}
{func_info}

{error_header}
{colored_text(error_details, Colors.WHITE)}
{"=" * 60}
"""


def view_test_wrapper(view_name: str):
    """Decorator for view tests that provides detailed failure messages."""

    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(self, *args, **kwargs):
            try:
                return test_func(self, *args, **kwargs)
            except Exception as e:
                # Extract function name from traceback
                tb = traceback.extract_tb(e.__traceback__)
                function_name = "unknown"
                for frame in reversed(tb):
                    if "controller" in frame.filename.lower():
                        function_name = frame.name
                        break

                # Create detailed failure message
                detailed_msg = detailed_failure_message(
                    test_name=test_func.__name__, view_name=view_name, function_name=function_name, error_details=f"{type(e).__name__}: {e!s}"
                )

                # Print the detailed message
                print(detailed_msg)

                # Re-raise the original exception
                raise

        return wrapper

    return decorator


def controller_test_wrapper(controller_name: str, method_name: str):
    """Decorator for controller method tests that provides detailed failure messages."""

    def decorator(test_func: Callable) -> Callable:
        @functools.wraps(test_func)
        def wrapper(self, *args, **kwargs):
            try:
                return test_func(self, *args, **kwargs)
            except Exception as e:
                # Create detailed failure message
                header = colored_text(safe_emoji_text("🚨 CONTROLLER TEST FAILURE! 🚨", "CONTROLLER TEST FAILURE!"), Colors.RED, bold=True)
                test_info = colored_text(f"Test: {test_func.__name__}", Colors.CYAN)
                controller_info = colored_text(f"Controller: {controller_name}", Colors.YELLOW)
                method_info = colored_text(f"Method: {method_name}", Colors.MAGENTA)
                error_header = colored_text(safe_emoji_text("💀 Error Details:", "Error Details:"), Colors.RED, bold=True)

                detailed_msg = f"""
{header}
{test_info}
{controller_info}
{method_info}

{error_header}
{colored_text(f"{type(e).__name__}: {e!s}", Colors.WHITE)}
{"=" * 60}
"""

                # Print the detailed message
                print(detailed_msg)

                # Re-raise the original exception
                raise

        return wrapper

    return decorator


class EnhancedTestResult(unittest.TestResult):
    """Custom TestResult class with enhanced failure reporting and colors."""

    def __init__(self, stream=None, descriptions=None, verbosity=None, **kwargs):
        super().__init__(stream, descriptions, verbosity)
        Colors.disable_on_windows_if_needed()
        self.stream = stream
        self.show_all = verbosity > 1
        self.dots = verbosity == 1

    def addError(self, test, err):
        super().addError(test, err)
        self._print_detailed_error(test, err, "ERROR")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._print_detailed_error(test, err, "FAILURE")

    def addSuccess(self, test):
        super().addSuccess(test)
        print(colored_text(safe_emoji_text(f"✅ {test._testMethodName}", f"OK {test._testMethodName}"), Colors.GREEN))

    def _print_detailed_error(self, test, err, error_type):
        """Print a detailed error message with colors."""
        exc_type, exc_value, exc_traceback = err

        # Extract relevant information
        test_name = test._testMethodName
        test_class = test.__class__.__name__
        error_msg = str(exc_value)

        # Create detailed header
        if error_type == "ERROR":
            header = colored_text(safe_emoji_text("💥 TEST ERROR! 💥", "TEST ERROR!"), Colors.RED, bold=True)
            emoji = safe_emoji_text("🔥", "ERROR:")
        else:
            header = colored_text(safe_emoji_text("❌ TEST FAILURE! ❌", "TEST FAILURE!"), Colors.YELLOW, bold=True)
            emoji = safe_emoji_text("💔", "FAILED:")

        # Format the message
        detailed_msg = f"""
{header}
{colored_text(f"Test Class: {test_class}", Colors.CYAN)}
{colored_text(f"Test Method: {test_name}", Colors.MAGENTA)}
{colored_text(f"Error Type: {exc_type.__name__}", Colors.YELLOW)}

{colored_text(f"{emoji} What went wrong:", Colors.RED, bold=True)}
{colored_text(error_msg, Colors.WHITE)}

{colored_text(safe_emoji_text("📍 Stack trace:", "Stack trace:"), Colors.BLUE, bold=True)}
"""

        print(detailed_msg)

        # Print a simplified stack trace with colors
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in tb_lines[-5:]:  # Show last 5 lines of traceback
            if 'File "' in line:
                print(colored_text(line.strip(), Colors.CYAN))
            elif line.strip().startswith(("assert", "self.assert")):
                print(colored_text(line.strip(), Colors.YELLOW))
            else:
                print(colored_text(line.strip(), Colors.WHITE))

        print(colored_text("=" * 60, Colors.BLUE))


class EnhancedTestRunner(unittest.TextTestRunner):
    """Custom test runner that uses EnhancedTestResult."""

    def __init__(self, *args, **kwargs):
        kwargs["resultclass"] = EnhancedTestResult
        kwargs["verbosity"] = 0  # We handle our own output
        super().__init__(*args, **kwargs)


def run_enhanced_tests(test_suite):
    """Run tests with enhanced failure reporting."""
    runner = EnhancedTestRunner()
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

    return result
