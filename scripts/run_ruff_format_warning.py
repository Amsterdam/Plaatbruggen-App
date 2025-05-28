#!/usr/bin/env python3
"""Ruff format wrapper that shows results but doesn't block push."""

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


def run_ruff_format_warning() -> int:
    """Run ruff format in check mode but always return success to allow push."""
    force_concise = should_use_concise_mode()

    try:
        # Run ruff format in check mode (don't modify files, just report)
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--check", "--config=.ruff.toml"],
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
                print(colored_text("✅ Code formatting is consistent", Colors.GREEN))  # noqa: T201
        else:
            # Check output for formatting issues
            output = (result.stdout or "") + (result.stderr or "")

            if force_concise:
                safe_emoji_text("⚠️  FORMATTING ISSUES", "FORMATTING ISSUES")
                print(colorized_status_message("Code formatting inconsistencies found", is_success=False, is_warning=True))  # noqa: T201
            else:
                print(colored_text("⚠️  Code formatting inconsistencies found", Colors.YELLOW, bold=True))  # noqa: T201
                print(colored_text("Run 'python scripts/run_ruff_format.py' to auto-fix", Colors.YELLOW))  # noqa: T201
                if output.strip():
                    print(colored_text("Files that need formatting:", Colors.YELLOW))  # noqa: T201
                    print(output)  # noqa: T201

    except Exception as e:
        if force_concise:
            safe_emoji_text("❌ RUFF FORMAT EXECUTION FAILED", "RUFF FORMAT EXECUTION FAILED")
        else:
            print(colored_text("❌ Error running ruff format", Colors.RED, bold=True))  # noqa: T201
        print(f"Error: {e}")  # noqa: T201

    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_ruff_format_warning())
