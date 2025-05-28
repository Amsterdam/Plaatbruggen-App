#!/usr/bin/env python3
"""Apply auto-fixes to code before pushing."""

import subprocess
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import (  # noqa: E402
    Colors,
    colored_text,
    safe_emoji_text,
    should_use_concise_mode,
)


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    try:
        subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")  # noqa: T201
        if e.stdout:
            print(e.stdout)  # noqa: T201
        if e.stderr:
            print(e.stderr)  # noqa: T201
        return False
    else:
        return True


def main() -> int:
    """Apply all auto-fixes."""
    force_concise = should_use_concise_mode()

    if not force_concise:
        print(colored_text("🔧 Applying code formatting and style fixes...", Colors.BLUE, bold=True))  # noqa: T201

    # Apply ruff formatting
    print("📝 Formatting code...")  # noqa: T201
    if not run_command([sys.executable, "-m", "ruff", "format", "--config=.ruff.toml"], "ruff format"):
        return 1

    # Apply ruff fixes
    print("🔧 Fixing code style issues...")  # noqa: T201
    if not run_command([sys.executable, "-m", "ruff", "check", "--fix", "--config=.ruff.toml"], "ruff check --fix"):
        return 1

    if not force_concise:
        print(colored_text("✅ All auto-fixes applied!", Colors.GREEN, bold=True))  # noqa: T201
        print(colored_text("Now you can commit and push your changes.", Colors.GREEN))  # noqa: T201
    else:
        safe_emoji_text("✅ AUTO-FIXES APPLIED", "AUTO-FIXES APPLIED")

    return 0


if __name__ == "__main__":
    sys.exit(main())
