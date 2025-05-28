#!/usr/bin/env python3
"""Ruff format wrapper with enhanced messaging for git hooks."""

import os
import subprocess
import sys
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import (  # noqa: E402
    Colors,
    colored_text,
    colorized_status_message,
    safe_arrow,
    safe_emoji_text,
    should_use_concise_mode,
)


def setup_environment() -> bool:
    """Set up environment and determine if concise mode should be used."""
    # Use the improved environment detection from test_utils
    force_concise = should_use_concise_mode()

    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

    return force_concise


def extract_format_stats(lines: list[str]) -> tuple[int, int]:
    """Extract formatting statistics from ruff format output."""
    reformatted = 0
    unchanged = 0

    for line in lines:
        if "reformatted" in line.lower() and "unchanged" in line.lower():
            # Parse line like "1 file reformatted, 56 files left unchanged"
            try:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in {"file", "files"} and i > 0 and parts[i - 1].isdigit():
                        if "reformatted" in line[: line.index(part)]:
                            reformatted = int(parts[i - 1])
                        elif "unchanged" in line[line.index(part) :]:
                            unchanged = int(parts[i - 1])
            except (IndexError, ValueError):
                pass

    return reformatted, unchanged


def handle_concise_output(result: subprocess.CompletedProcess) -> None:
    """Handle output in concise mode for git hooks."""
    output = (result.stdout or "") + (result.stderr or "")
    lines = output.strip().split("\n") if output else []

    reformatted, _ = extract_format_stats(lines)

    # Check if files were actually reformatted (regardless of exit code)
    if reformatted > 0:
        # Files were reformatted
        safe_emoji_text("⚠️ FILES REFORMATTED", "FILES REFORMATTED")
        print(colorized_status_message(f"Warning: {reformatted} file(s) were reformatted", is_success=False, is_warning=True))  # noqa: T201
        print(colorized_status_message("Consider committing the formatting changes", is_success=False, is_warning=True))  # noqa: T201
    elif result.returncode == 0:
        safe_emoji_text("✅ RUFF FORMAT PASSED!", "RUFF FORMAT PASSED!")
        print(colorized_status_message("Code formatting is consistent", is_success=True))  # noqa: T201
    else:
        safe_emoji_text("⚠️ RUFF FORMAT WARNING", "RUFF FORMAT WARNING")
        print(colorized_status_message("Warning: Code formatting check had issues", is_success=False, is_warning=True))  # noqa: T201


def run_ruff_format() -> int:
    """Run ruff format and provide enhanced messaging."""
    force_concise = setup_environment()

    try:
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
        reformatted, _ = extract_format_stats(lines)

        if reformatted > 0 and result.returncode == 0:
            # Files were reformatted - show warning but allow push to continue
            if force_concise:
                safe_emoji_text("⚠️ FILES REFORMATTED", "FILES REFORMATTED")
                print(colorized_status_message(f"Warning: {reformatted} file(s) were reformatted", is_success=False, is_warning=True))  # noqa: T201
                print(colorized_status_message("Consider committing the formatting changes before pushing", is_success=False, is_warning=True))  # noqa: T201
            else:
                print(colored_text(f"⚠️ Warning: {reformatted} file(s) were reformatted", Colors.YELLOW, bold=True))  # noqa: T201
                print(colored_text("Consider committing these formatting changes:", Colors.YELLOW))  # noqa: T201
                print(f"  {colored_text('git add .', Colors.CYAN)}")  # noqa: T201
                print(f"  {colored_text('git commit -m \"Apply code formatting\"', Colors.CYAN)}")  # noqa: T201
            # Return success anyway - this is just a warning
            return 0

        if force_concise:
            handle_concise_output(result)
        elif result.stdout:
            print(result.stdout)  # noqa: T201

        if result.stderr:
            print(result.stderr, file=sys.stderr)  # noqa: T201

    except Exception as e:
        safe_emoji_text("❌ RUFF FORMAT EXECUTION FAILED", "RUFF FORMAT EXECUTION FAILED")
        print(f"Error running ruff format: {e}")  # noqa: T201
        # Even on execution failure, return success for warning-only mode
        return 0
    else:
        # Always return success for warning-only mode
        return 0


if __name__ == "__main__":
    sys.exit(run_ruff_format())
