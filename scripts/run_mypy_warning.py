#!/usr/bin/env python3
"""MyPy wrapper that shows results but doesn't block push."""

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


def run_mypy_warning() -> int:
    """Run mypy but always return success to allow push."""
    force_concise = should_use_concise_mode()
    
    try:
        # Run mypy directly
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "app", "src"],
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
                print(colored_text("✅ No type checking issues found", Colors.GREEN))  # noqa: T201
        else:
            # Count errors and warnings
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []
            
            error_count = 0
            for line in lines:
                if ": error:" in line or ": warning:" in line:
                    error_count += 1

            if force_concise:
                safe_emoji_text("❌ TYPE CHECKING ISSUES", "TYPE CHECKING ISSUES")
                if error_count > 0:
                    print(colorized_status_message(f"Found {error_count} type checking issues", is_success=False, is_warning=True))  # noqa: T201
                else:
                    print(colorized_status_message("Type checking issues found", is_success=False, is_warning=True))  # noqa: T201
            else:
                print(colored_text("❌ Type checking issues found", Colors.RED, bold=True))  # noqa: T201
                if error_count > 0:
                    print(colored_text(f"Found {error_count} issue(s)", Colors.YELLOW))  # noqa: T201
                if result.stdout:
                    print(result.stdout)  # noqa: T201
                if result.stderr:
                    print(result.stderr, file=sys.stderr)  # noqa: T201

    except Exception as e:
        if force_concise:
            safe_emoji_text("❌ MYPY EXECUTION FAILED", "MYPY EXECUTION FAILED")
        else:
            print(colored_text("❌ Error running mypy", Colors.RED, bold=True))  # noqa: T201
        print(f"Error: {e}")  # noqa: T201

    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_mypy_warning())
