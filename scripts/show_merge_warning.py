#!/usr/bin/env python3
"""Show merge warning when code quality checks have issues."""

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
    safe_emoji_text,
    should_use_concise_mode,
)


def setup_environment() -> bool:
    """Set up environment and determine if concise mode should be used."""
    force_concise = should_use_concise_mode()

    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ["MSYSTEM", "MINGW_PREFIX", "TERM"]):
        os.environ["FORCE_COLOR"] = "1"

    return force_concise


def run_check_script(script_name: str) -> tuple[int, str]:
    """Run a check script and return exit code and output."""
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, f"Error running {script_name}: {e}"


def show_merge_warning() -> int:
    """Show warning about potential merge issues but don't block push."""
    force_concise = setup_environment()
    
    # Check all quality scripts
    checks = [
        ("run_ruff_check.py", "Code style"),
        ("run_ruff_format.py", "Code formatting"), 
        ("run_mypy.py", "Type checking"),
        ("../run_enhanced_tests.py", "Unit tests"),
    ]
    
    failed_checks = []
    
    if not force_concise:
        print(colored_text("🔍 Running code quality checks...", Colors.BLUE, bold=True))  # noqa: T201
    
    for script, name in checks:
        exit_code, _ = run_check_script(script)
        if exit_code != 0:
            failed_checks.append(name)
    
    if failed_checks:
        if force_concise:
            safe_emoji_text("⚠️  CODE QUALITY WARNING", "CODE QUALITY WARNING")
            print(f"Issues found: {', '.join(failed_checks)}")  # noqa: T201
            print("This branch may not be mergeable with development!")  # noqa: T201
            print("Consider running: python scripts/run_ruff_check.py")  # noqa: T201
        else:
            print()  # noqa: T201
            print(colored_text("⚠️  CODE QUALITY WARNING", Colors.YELLOW, bold=True))  # noqa: T201
            print(colored_text("="*60, Colors.YELLOW))  # noqa: T201
            print(colored_text("The following checks found issues:", Colors.YELLOW))  # noqa: T201
            for check in failed_checks:
                print(f"  • {colored_text(check, Colors.RED)}")  # noqa: T201
            print()  # noqa: T201
            print(colored_text("⚠️  This branch may not be able to merge with development!", Colors.YELLOW, bold=True))  # noqa: T201
            print(colored_text("Consider fixing these issues before creating a pull request.", Colors.YELLOW))  # noqa: T201
            print(colored_text("="*60, Colors.YELLOW))  # noqa: T201
    else:
        if not force_concise:
            print(colored_text("✅ All code quality checks passed!", Colors.GREEN, bold=True))  # noqa: T201
            print(colored_text("This branch should be ready to merge with development.", Colors.GREEN))  # noqa: T201
    
    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(show_merge_warning()) 