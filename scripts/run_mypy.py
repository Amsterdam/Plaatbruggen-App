#!/usr/bin/env python3
"""
MyPy wrapper with concise summary for git hooks.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import Colors, colored_text, safe_emoji_text, should_use_concise_mode


def run_mypy():
    """Run mypy and provide concise summary."""
    # Force concise mode for pre-commit by detecting if we're running in a subprocess
    # This is a fallback in case our environment detection doesn't work
    is_subprocess = os.environ.get("_") != sys.executable
    force_concise = is_subprocess or should_use_concise_mode()

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "."], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=project_root, check=False
        )

        if force_concise:
            # Combine stdout and stderr for analysis
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []

            if result.returncode == 0:
                success_msg = safe_emoji_text("✅ MYPY CHECK PASSED!", "MYPY CHECK PASSED!")
                print(colored_text(success_msg, Colors.GREEN, bold=True))
                detail_msg = "Type checking: No issues found"
                print(colored_text(detail_msg, Colors.GREEN))
            else:
                fail_msg = safe_emoji_text("❌ MYPY CHECK FAILED", "MYPY CHECK FAILED")
                print(colored_text(fail_msg, Colors.RED, bold=True))

                # Count errors from output
                error_lines = [line for line in lines if ": error:" in line or ": note:" in line]
                error_count = len([line for line in lines if ": error:" in line])

                count_msg = f"Type checking: {error_count} errors found"
                print(colored_text(count_msg, Colors.RED))
                help_msg = "\nFor detailed output, run:"
                print(colored_text(help_msg, Colors.CYAN))
                cmd_msg = "  python -m mypy ."
                print(colored_text(cmd_msg, Colors.WHITE))
        else:
            # In detailed mode, show full output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return result.returncode

    except Exception as e:
        error_msg = f"Error running mypy: {e}"
        print(error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(run_mypy())
