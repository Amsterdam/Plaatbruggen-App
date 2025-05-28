#!/usr/bin/env python3
"""Ruff check wrapper that shows results but doesn't block push."""

import subprocess
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import (  # noqa: E402
    Colors,
    colored_text,
    colorized_status_message,
    safe_emoji_text,
    should_use_concise_mode,
)


def run_ruff_check_warning() -> int:
    """Run ruff check but always return success to allow push."""
    force_concise = should_use_concise_mode()

    try:
        # Run ruff check directly without auto-push logic
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--config=.ruff.toml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )

        # Show results
        if result.returncode == 0:
            if not force_concise:
                print(colored_text("✅ No code style issues found", Colors.GREEN))  # noqa: T201
        else:
            # Count violations
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []

            violation_count = 0
            for line in lines:
                if "Found" in line and "violation" in line:
                    try:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                violation_count = int(part)
                                break
                    except (IndexError, ValueError):
                        pass

            if force_concise:
                safe_emoji_text("❌ CODE STYLE ISSUES", "CODE STYLE ISSUES")
                if violation_count > 0:
                    print(colorized_status_message(f"Found {violation_count} code style issues", is_success=False, is_warning=True))  # noqa: T201
                else:
                    print(colorized_status_message("Code style issues found", is_success=False, is_warning=True))  # noqa: T201
            else:
                print(colored_text("❌ Code style issues found", Colors.RED, bold=True))  # noqa: T201
                if violation_count > 0:
                    print(colored_text(f"Found {violation_count} violation(s)", Colors.YELLOW))  # noqa: T201
                if result.stdout:
                    print(result.stdout)  # noqa: T201
                if result.stderr:
                    print(result.stderr, file=sys.stderr)  # noqa: T201

    except Exception as e:
        if force_concise:
            safe_emoji_text("❌ RUFF CHECK EXECUTION FAILED", "RUFF CHECK EXECUTION FAILED")
        else:
            print(colored_text("❌ Error running ruff check", Colors.RED, bold=True))  # noqa: T201
        print(f"Error: {e}")  # noqa: T201

    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_ruff_check_warning())
