#!/usr/bin/env python3
"""
MyPy wrapper with concise summary for git hooks.
"""

import subprocess
import sys
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import Colors, colored_text, safe_emoji_text, should_use_concise_mode


def run_mypy():
    """Run mypy and provide concise summary."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root, check=False
        )

        if should_use_concise_mode():
            # Combine stdout and stderr for analysis
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []

            if result.returncode == 0:
                print(colored_text(safe_emoji_text("✅ MYPY CHECK PASSED!", "MYPY CHECK PASSED!"), Colors.GREEN, bold=True))
                print(colored_text("Type checking: No issues found", Colors.GREEN))
            else:
                print(colored_text(safe_emoji_text("❌ MYPY CHECK FAILED", "MYPY CHECK FAILED"), Colors.RED, bold=True))

                # Count errors from output
                error_lines = [line for line in lines if ": error:" in line or ": note:" in line]
                error_count = len([line for line in lines if ": error:" in line])

                print(colored_text(f"Type checking: {error_count} errors found", Colors.RED))
                print(colored_text("\nFor detailed output, run:", Colors.CYAN))
                print(colored_text("  python -m mypy .", Colors.WHITE))
        else:
            # In detailed mode, show full output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return result.returncode

    except Exception as e:
        print(colored_text(f"Error running mypy: {e}", Colors.RED))
        return 1


if __name__ == "__main__":
    sys.exit(run_mypy())
