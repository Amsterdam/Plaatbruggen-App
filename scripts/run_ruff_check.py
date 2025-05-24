#!/usr/bin/env python3
"""Ruff check wrapper with concise summary for git hooks."""

import os
import subprocess
import sys
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import safe_emoji_text, should_use_concise_mode  # noqa: E402


def setup_environment() -> bool:
    """Set up environment and determine if concise mode should be used."""
    # Force concise mode for pre-commit by detecting if we're running in a subprocess
    # This is a fallback in case our environment detection doesn't work
    is_subprocess = os.environ.get("_") != sys.executable
    force_concise = is_subprocess or should_use_concise_mode()

    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

    return force_concise


def extract_error_count(lines: list[str]) -> int:
    """Extract error count from ruff output lines."""
    error_count = 0

    # Try to extract from "Found X errors" line
    for line in lines:
        if "Found" in line and ("error" in line or "issue" in line):
            try:
                words = line.split()
                for i, word in enumerate(words):
                    if word == "Found" and i + 1 < len(words):
                        error_count = int(words[i + 1])
                        break
            except (IndexError, ValueError):
                pass

    # Fallback: count actual error lines
    if error_count == 0:
        error_lines = [line for line in lines if line.strip() and (":" in line) and not line.startswith("Found") and not line.startswith("No fixes")]
        error_count = len(error_lines)

    return error_count


def handle_concise_output(result: subprocess.CompletedProcess) -> None:
    """Handle output in concise mode for git hooks."""
    if result.returncode == 0:
        safe_emoji_text("✅ RUFF CHECK PASSED!", "RUFF CHECK PASSED!")
        print("No code style issues found")  # noqa: T201
    else:
        safe_emoji_text("❌ RUFF CHECK FAILED", "RUFF CHECK FAILED")

        # Combine stdout and stderr for analysis
        output = (result.stdout or "") + (result.stderr or "")
        lines = output.strip().split("\n") if output else []

        # Extract error count
        error_count = extract_error_count(lines)

        if error_count > 0:
            print(f"Found {error_count} code style issues")  # noqa: T201

            # Show first few error lines for context
            error_lines = [
                line for line in lines if line.strip() and (":" in line) and not line.startswith("Found") and not line.startswith("No fixes")
            ]
            if error_lines:
                print("First few issues:")  # noqa: T201
                for error in error_lines[:3]:
                    print(f"  {error}")  # noqa: T201
                if len(error_lines) > 3:
                    print(f"  ... and {len(error_lines) - 3} more issues")  # noqa: T201
        else:
            print("Code style check failed but no specific errors found")  # noqa: T201


def run_ruff_check() -> int:
    """Run ruff check and provide concise summary."""
    force_concise = setup_environment()

    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--config=.ruff.toml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )

        if force_concise:
            handle_concise_output(result)
        else:
            # In detailed mode, show full output
            if result.stdout:
                print(result.stdout)  # noqa: T201
            if result.stderr:
                print(result.stderr, file=sys.stderr)  # noqa: T201

    except Exception as e:
        safe_emoji_text("❌ RUFF EXECUTION FAILED", "RUFF EXECUTION FAILED")
        print(f"Error running ruff: {e}")  # noqa: T201
        return 1
    else:
        return result.returncode


if __name__ == "__main__":
    sys.exit(run_ruff_check())
