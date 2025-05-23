#!/usr/bin/env python3
"""
Ruff check wrapper with concise summary for git hooks.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add the project root to Python path to access test utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import Colors, colored_text, safe_emoji_text, should_use_concise_mode


def run_ruff_check():
    """Run ruff check and provide concise summary."""
    # Force concise mode for pre-commit by detecting if we're running in a subprocess
    # This is a fallback in case our environment detection doesn't work
    is_subprocess = os.environ.get("_") != sys.executable
    force_concise = is_subprocess or should_use_concise_mode()
    
    # Enable colors for Git environments (like Git Bash) even if detection is conservative
    if any(os.environ.get(var) for var in ['MSYSTEM', 'MINGW_PREFIX', 'TERM']):
        os.environ["FORCE_COLOR"] = "1"
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--config=.ruff.toml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )

        if force_concise:
            # Combine stdout and stderr for analysis
            output = (result.stdout or "") + (result.stderr or "")
            lines = output.strip().split("\n") if output else []

            if result.returncode == 0:
                success_msg = safe_emoji_text("✅ RUFF CHECK PASSED!", "RUFF CHECK PASSED!")
                print(colored_text(success_msg, Colors.GREEN, bold=True))
                detail_msg = "Code style: No issues found"
                print(colored_text(detail_msg, Colors.GREEN))
            else:
                fail_msg = safe_emoji_text("❌ RUFF CHECK FAILED", "RUFF CHECK FAILED")
                print(colored_text(fail_msg, Colors.RED, bold=True))

                # Try to extract error count from output
                error_count = 0
                for line in lines:
                    if "Found" in line and ("error" in line or "issue" in line):
                        try:
                            # Extract number from "Found X errors" or similar
                            words = line.split()
                            for i, word in enumerate(words):
                                if word == "Found" and i + 1 < len(words):
                                    error_count = int(words[i + 1])
                                    break
                        except (IndexError, ValueError):
                            pass

                if error_count == 0:
                    # Count actual error lines as fallback
                    error_lines = [
                        line for line in lines if line.strip() and (":" in line) and not line.startswith("Found") and not line.startswith("No fixes")
                    ]
                    error_count = len(error_lines)

                count_msg = f"Code style: {error_count} issues found"
                print(colored_text(count_msg, Colors.RED))
                help_msg = "\nFor detailed output, run:"
                print(colored_text(help_msg, Colors.CYAN))
                cmd_msg = "  python -m ruff check --config=.ruff.toml"
                print(colored_text(cmd_msg, Colors.WHITE))
        else:
            # In detailed mode, show full output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return result.returncode

    except Exception as e:
        error_msg = f"Error running ruff: {e}"
        print(error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(run_ruff_check())
