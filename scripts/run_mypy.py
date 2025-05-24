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


def run_mypy() -> int:
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
            else:
                safe_emoji_text("❌ MYPY CHECK FAILED", "MYPY CHECK FAILED")

                # Count errors from output
                [line for line in lines if ": error:" in line or ": note:" in line]
                len([line for line in lines if ": error:" in line])

        else:
            # In detailed mode, show full output
            if result.stdout:
                pass
            if result.stderr:
                pass

    except Exception:
        return 1
    else:
        return result.returncode


if __name__ == "__main__":
    sys.exit(run_mypy())
