#!/usr/bin/env python3
"""MyPy wrapper with concise summary for git hooks."""

import os
import subprocess
import sys
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import safe_emoji_text, should_use_concise_mode  # noqa: E402


def run_mypy() -> int:  # noqa: PLR0912, C901
    """Run mypy and provide concise summary."""
    # Force concise mode for pre-commit by detecting if we're running in a subprocess
    # This is a fallback in case our environment detection doesn't work
    is_subprocess = os.environ.get("_") != sys.executable
    force_concise = is_subprocess or should_use_concise_mode()

    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "."], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=project_root, check=False
        )

        if force_concise:
            # Combine stdout and stderr for analysis
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []

            if result.returncode == 0:
                safe_emoji_text("✅ MYPY CHECK PASSED!", "MYPY CHECK PASSED!")
                print("No type checking issues found")  # noqa: T201
            else:
                safe_emoji_text("❌ MYPY CHECK FAILED", "MYPY CHECK FAILED")

                # Count errors from output
                error_lines = [line for line in lines if ": error:" in line]
                error_count = len(error_lines)
                note_lines = [line for line in lines if ": note:" in line]
                note_count = len(note_lines)

                if error_count > 0:
                    print(f"Found {error_count} type checking errors")  # noqa: T201
                if note_count > 0:
                    print(f"Found {note_count} type checking notes")  # noqa: T201

                # Show first few errors for context
                if error_lines:
                    print("First few errors:")  # noqa: T201
                    for error in error_lines[:3]:
                        print(f"  {error}")  # noqa: T201
                    if len(error_lines) > 3:
                        print(f"  ... and {len(error_lines) - 3} more errors")  # noqa: T201

        else:
            # In detailed mode, show full output
            if result.stdout:
                print(result.stdout)  # noqa: T201
            if result.stderr:
                print(result.stderr, file=sys.stderr)  # noqa: T201

    except Exception as e:
        safe_emoji_text("❌ MYPY EXECUTION FAILED", "MYPY EXECUTION FAILED")
        print(f"Error running mypy: {e}")  # noqa: T201
        return 1
    else:
        return result.returncode


if __name__ == "__main__":
    sys.exit(run_mypy())
