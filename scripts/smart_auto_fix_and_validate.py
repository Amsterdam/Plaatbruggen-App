#!/usr/bin/env python3
"""Smart auto-fix and validate script for seamless git push experience."""

import os
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


def is_git_hook_environment() -> bool:
    """Check if we're running in a git hook environment."""
    return any(var in os.environ for var in ["PRE_COMMIT", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL"]) or any(
        term in str(sys.argv[0]).lower() for term in ["pre-commit", "hook"]
    )


def run_command_with_output(cmd: list[str], description: str) -> tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )
        return result.returncode, (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return 1, f"Error running {description}: {e}"


def has_unstaged_changes() -> bool:
    """Check if there are unstaged changes."""
    exit_code, output = run_command_with_output(["git", "diff", "--name-only"], "git diff")
    return exit_code == 0 and output.strip() != ""


def has_staged_changes() -> bool:
    """Check if there are staged changes."""
    exit_code, output = run_command_with_output(["git", "diff", "--cached", "--name-only"], "git diff --cached")
    return exit_code == 0 and output.strip() != ""


def stage_all_changes() -> bool:
    """Stage all changes."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=project_root, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def commit_changes(message: str) -> bool:
    """Commit staged changes."""
    try:
        subprocess.run(["git", "commit", "-m", message], cwd=project_root, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def apply_ruff_formatting() -> tuple[bool, int]:
    """Apply ruff formatting and return (success, files_changed)."""
    exit_code, output = run_command_with_output([sys.executable, "-m", "ruff", "format", "--config=.ruff.toml"], "ruff format")

    # Count reformatted files
    files_changed = 0
    for line in output.split("\n"):
        if "reformatted" in line.lower():
            try:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in {"file", "files"} and i > 0 and parts[i - 1].isdigit():
                        files_changed = int(parts[i - 1])
                        break
            except (IndexError, ValueError):
                pass

    return exit_code == 0, files_changed


def apply_ruff_fixes() -> tuple[bool, int]:
    """Apply ruff style fixes and return (success, issues_fixed)."""
    exit_code, output = run_command_with_output([sys.executable, "-m", "ruff", "check", "--fix", "--config=.ruff.toml"], "ruff check --fix")

    # Count fixed issues
    issues_fixed = 0
    for line in output.split("\n"):
        if "Fixed" in line:
            try:
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        issues_fixed = int(part)
                        break
            except (IndexError, ValueError):
                pass

    return exit_code == 0, issues_fixed


def run_quality_checks() -> tuple[bool, bool, bool]:
    """Run quality checks and return (ruff_clean, mypy_clean, tests_clean)."""
    # Check ruff (style and formatting)
    ruff_exit, _ = run_command_with_output([sys.executable, "-m", "ruff", "check", "--config=.ruff.toml"], "ruff check")
    format_exit, _ = run_command_with_output([sys.executable, "-m", "ruff", "format", "--check", "--config=.ruff.toml"], "ruff format --check")

    # Check mypy
    mypy_exit, _ = run_command_with_output([sys.executable, "-m", "mypy", "app", "src"], "mypy")

    # Run tests
    test_exit, _ = run_command_with_output([sys.executable, "run_enhanced_tests.py"], "tests")

    return (ruff_exit == 0 and format_exit == 0), mypy_exit == 0, test_exit == 0


def apply_formatting_step(force_concise: bool) -> tuple[bool, int]:
    """Apply formatting and return success status and files changed."""
    if not force_concise:
        print(colored_text("Applying code formatting...", Colors.CYAN))  # noqa: T201

    format_success, files_formatted = apply_ruff_formatting()
    if not format_success:
        print(colored_text("Code formatting failed", Colors.RED))  # noqa: T201
        return False, files_formatted

    if files_formatted > 0 and not force_concise:
        print(colored_text(f"Formatted {files_formatted} file(s)", Colors.YELLOW))  # noqa: T201

    return True, files_formatted


def apply_style_fixes_step(force_concise: bool) -> tuple[bool, int]:
    """Apply style fixes and return success status and issues fixed."""
    if not force_concise:
        print(colored_text("Applying style fixes...", Colors.CYAN))  # noqa: T201

    style_success, issues_fixed = apply_ruff_fixes()
    if not style_success:
        print(colored_text("Style fixes failed", Colors.RED))  # noqa: T201
        return False, issues_fixed

    if issues_fixed > 0 and not force_concise:
        print(colored_text(f"Fixed {issues_fixed} style issue(s)", Colors.YELLOW))  # noqa: T201

    return True, issues_fixed


def commit_auto_fixes(files_formatted: int, issues_fixed: int, force_concise: bool) -> bool:
    """Commit auto-fixes if any were made."""
    changes_made = files_formatted > 0 or issues_fixed > 0
    if not changes_made:
        return True

    if has_unstaged_changes() and not stage_all_changes():
        print(colored_text("Failed to stage auto-fix changes", Colors.RED))  # noqa: T201
        return False

    commit_msg = f"Auto-fix code quality ({files_formatted} formatted, {issues_fixed} style fixes)"
    if commit_changes(commit_msg):
        if not force_concise:
            print(colored_text("Auto-fixes committed", Colors.GREEN))  # noqa: T201
        return True
    print(colored_text("Failed to commit auto-fixes", Colors.RED))  # noqa: T201
    return False


def report_results(ruff_clean: bool, mypy_clean: bool, tests_clean: bool, changes_made: bool, force_concise: bool) -> int:
    """Report final results and return exit code."""
    if ruff_clean and mypy_clean and tests_clean:
        if force_concise:
            if changes_made:
                safe_emoji_text("AUTO-FIXED & VALIDATED", "AUTO-FIXED & VALIDATED")
            else:
                safe_emoji_text("ALL CHECKS PASSED", "ALL CHECKS PASSED")
        else:
            print(colored_text("All quality checks passed!", Colors.GREEN, bold=True))  # noqa: T201
            if changes_made:
                print(colored_text("Auto-fixes have been applied and committed.", Colors.GREEN))  # noqa: T201
            print(colored_text("Push will proceed...", Colors.GREEN))  # noqa: T201
        return 0


    # Show what failed
    failures = []
    if not ruff_clean:
        failures.append("Code style/formatting")
    if not mypy_clean:
        failures.append("Type checking")
    if not tests_clean:
        failures.append("Tests")

    if force_concise:
        safe_emoji_text("QUALITY CHECKS FAILED", "QUALITY CHECKS FAILED")
        print(f"Failed: {', '.join(failures)}")  # noqa: T201
    else:
        print(colored_text("Quality checks failed - push blocked", Colors.RED, bold=True))  # noqa: T201
        print(colored_text(f"Failed checks: {', '.join(failures)}", Colors.YELLOW))  # noqa: T201
        print(colored_text("Please fix the remaining issues manually:", Colors.CYAN))  # noqa: T201
        print(colored_text("  • Run 'python -m ruff check .' for style issues", Colors.CYAN))  # noqa: T201
        print(colored_text("  • Run 'python -m mypy app src' for type issues", Colors.CYAN))  # noqa: T201
        print(colored_text("  • Run 'python run_enhanced_tests.py' for test failures", Colors.CYAN))  # noqa: T201

    return 1


def main() -> int:
    """Main execution function."""
    force_concise = should_use_concise_mode()

    if not force_concise:
        print(colored_text("Smart Auto-Fix and Validate", Colors.BLUE, bold=True))  # noqa: T201
        print(colored_text("Checking and fixing code quality issues...", Colors.BLUE))  # noqa: T201

    # Step 1: Apply formatting fixes
    format_success, files_formatted = apply_formatting_step(force_concise)
    if not format_success:
        return 1

    # Step 2: Apply style fixes
    style_success, issues_fixed = apply_style_fixes_step(force_concise)
    if not style_success:
        return 1

    # Step 3: Commit auto-fixes if any were made
    if not commit_auto_fixes(files_formatted, issues_fixed, force_concise):
        return 1

    # Step 4: Run quality validation checks
    if not force_concise:
        print(colored_text("Running quality checks...", Colors.CYAN))  # noqa: T201

    ruff_clean, mypy_clean, tests_clean = run_quality_checks()

    # Step 5: Report results
    changes_made = files_formatted > 0 or issues_fixed > 0
    return report_results(ruff_clean, mypy_clean, tests_clean, changes_made, force_concise)


if __name__ == "__main__":
    sys.exit(main())
