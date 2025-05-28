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
    """Run ruff format but always return success to allow push."""
    force_concise = should_use_concise_mode()
    
    try:
        # Run ruff format directly without auto-push logic
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--config=.ruff.toml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )

        # Check if files were reformatted
        output = (result.stdout or "") + (result.stderr or "")
        lines = output.strip().split("\n") if output else []
        
        reformatted = 0
        for line in lines:
            if "reformatted" in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part in {"file", "files"} and i > 0 and parts[i - 1].isdigit():
                            if "reformatted" in line[:line.index(part)]:
                                reformatted = int(parts[i - 1])
                                break
                except (IndexError, ValueError):
                    pass

        # Show results but don't auto-commit/push
        if reformatted > 0:
            if force_concise:
                safe_emoji_text("🔧 FILES REFORMATTED", "FILES REFORMATTED")
                print(colorized_status_message(f"Reformatted {reformatted} file(s)", is_success=True, is_warning=True))  # noqa: T201
            else:
                print(colored_text("🔧 Auto-formatting applied", Colors.YELLOW, bold=True))  # noqa: T201
                print(colored_text(f"Reformatted {reformatted} file(s)", Colors.GREEN))  # noqa: T201
        elif result.returncode == 0:
            if not force_concise:
                print(colored_text("✅ Code formatting is consistent", Colors.GREEN))  # noqa: T201
        else:
            if force_concise:
                safe_emoji_text("❌ RUFF FORMAT FAILED", "RUFF FORMAT FAILED")
            else:
                print(colored_text("❌ Code formatting failed", Colors.RED, bold=True))  # noqa: T201
                if result.stderr:
                    print(result.stderr, file=sys.stderr)  # noqa: T201

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
