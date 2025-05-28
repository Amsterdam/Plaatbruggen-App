#!/usr/bin/env python3
"""Auto-fix code quality issues and push when clean."""

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


def has_changes_to_commit() -> bool:
    """Check if there are any changes to commit."""
    exit_code, output = run_command_with_output(["git", "status", "--porcelain"], "git status")
    return exit_code == 0 and output.strip() != ""


def commit_changes(message: str) -> bool:
    """Commit all changes with the given message."""
    if not has_changes_to_commit():
        return True  # No changes to commit is considered success

    try:
        subprocess.run(["git", "add", "-A"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=project_root, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def run_ruff_format() -> tuple[bool, int]:
    """Run ruff format and return (success, files_changed)."""
    exit_code, output = run_command_with_output([sys.executable, "-m", "ruff", "format", "--config=.ruff.toml"], "ruff format")

    # Count reformatted files
    files_changed = 0
    for line in output.split("\n"):
        if "reformatted" in line.lower():
            try:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in {"file", "files"} and i > 0 and parts[i - 1].isdigit() and "reformatted" in line[: line.index(part)]:
                        files_changed = int(parts[i - 1])
                        break
            except (IndexError, ValueError):
                pass

    return exit_code == 0, files_changed


def run_ruff_check_fix() -> tuple[bool, int]:
    """Run ruff check with auto-fix and return (success, issues_fixed)."""
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
    """Run all quality checks and return (ruff_check_clean, mypy_clean, tests_clean)."""
    # Check ruff style issues (without fixing)
    ruff_exit, _ = run_command_with_output([sys.executable, "-m", "ruff", "check", "--config=.ruff.toml"], "ruff check")

    # Check formatting
    format_exit, _ = run_command_with_output([sys.executable, "-m", "ruff", "format", "--check", "--config=.ruff.toml"], "ruff format --check")

    # Check mypy
    mypy_exit, _ = run_command_with_output([sys.executable, "-m", "mypy", "app", "src"], "mypy")

    # Run tests
    test_exit, _ = run_command_with_output([sys.executable, "run_enhanced_tests.py"], "tests")

    return (ruff_exit == 0 and format_exit == 0), mypy_exit == 0, test_exit == 0


def show_progress(iteration: int, force_concise: bool) -> None:
    """Show iteration progress."""
    if not force_concise:
        print(f"\n{colored_text(f'--- Iteration {iteration} ---', Colors.CYAN, bold=True)}")  # noqa: T201


def handle_formatting(force_concise: bool) -> tuple[bool, int]:
    """Handle ruff formatting step."""
    format_success, files_formatted = run_ruff_format()
    if files_formatted > 0:
        if not force_concise:
            print(colored_text(f"🔧 Formatted {files_formatted} file(s)", Colors.YELLOW))  # noqa: T201

        commit_msg = f"Auto-format code ({files_formatted} file{'s' if files_formatted != 1 else ''})"
        if commit_changes(commit_msg):
            if not force_concise:
                print(colored_text("✅ Formatting changes committed", Colors.GREEN))  # noqa: T201
        else:
            print(colored_text("❌ Failed to commit formatting changes", Colors.RED))  # noqa: T201
            return False, files_formatted

    return True, files_formatted


def handle_style_fixes(force_concise: bool) -> tuple[bool, int]:
    """Handle ruff style fix step."""
    check_success, issues_fixed = run_ruff_check_fix()
    if issues_fixed > 0:
        if not force_concise:
            print(colored_text(f"🔧 Fixed {issues_fixed} code style issue(s)", Colors.YELLOW))  # noqa: T201

        commit_msg = f"Auto-fix code style issues ({issues_fixed} issue{'s' if issues_fixed != 1 else ''})"
        if commit_changes(commit_msg):
            if not force_concise:
                print(colored_text("✅ Style fix changes committed", Colors.GREEN))  # noqa: T201
        else:
            print(colored_text("❌ Failed to commit style fixes", Colors.RED))  # noqa: T201
            return False, issues_fixed

    return True, issues_fixed


def handle_successful_push(force_concise: bool) -> int:
    """Handle successful completion and push."""
    if not force_concise:
        print(colored_text("\n🎉 All quality checks passed!", Colors.GREEN, bold=True))  # noqa: T201
        print(colored_text("📤 Pushing to remote...", Colors.BLUE))  # noqa: T201

    try:
        subprocess.run(["git", "push"], cwd=project_root, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if force_concise:
            safe_emoji_text("❌ PUSH FAILED", "PUSH FAILED")
        else:
            print(colored_text("❌ Push failed", Colors.RED, bold=True))  # noqa: T201
        print(f"Git push error: {e}")  # noqa: T201
        return 1
    else:
        if force_concise:
            safe_emoji_text("✅ PUSH SUCCESSFUL", "PUSH SUCCESSFUL")
            print("All quality issues auto-fixed and pushed!")  # noqa: T201
        else:
            print(colored_text("✅ Push successful!", Colors.GREEN, bold=True))  # noqa: T201
            print(colored_text("All quality issues have been auto-fixed and committed.", Colors.GREEN))  # noqa: T201
        return 0


def show_remaining_issues(ruff_clean: bool, mypy_clean: bool, tests_clean: bool, force_concise: bool) -> None:
    """Show remaining issues that couldn't be auto-fixed."""
    if force_concise:
        return

    remaining_issues = []
    if not ruff_clean:
        remaining_issues.append("Code style/formatting")
    if not mypy_clean:
        remaining_issues.append("Type checking")
    if not tests_clean:
        remaining_issues.append("Tests")

    if remaining_issues:
        print(colored_text(f"⚠️  Remaining issues: {', '.join(remaining_issues)}", Colors.YELLOW))  # noqa: T201


def show_manual_fix_instructions(force_concise: bool) -> None:
    """Show instructions for manual fixes."""
    if force_concise:
        safe_emoji_text("❌ AUTO-FIX INCOMPLETE", "AUTO-FIX INCOMPLETE")
        print("Some issues require manual fixing.")  # noqa: T201
        print("Run: python scripts/run_ruff_check.py")  # noqa: T201
    else:
        print(colored_text("\n❌ Could not auto-fix all issues", Colors.RED, bold=True))  # noqa: T201
        print(colored_text("Some issues require manual intervention:", Colors.YELLOW))  # noqa: T201
        print(colored_text("  • Run 'python scripts/run_ruff_check.py' for detailed code style issues", Colors.CYAN))  # noqa: T201
        print(colored_text("  • Run 'python scripts/run_mypy.py' for type checking issues", Colors.CYAN))  # noqa: T201
        print(colored_text("  • Run 'python run_enhanced_tests.py' for test failures", Colors.CYAN))  # noqa: T201


def auto_fix_and_push() -> int:
    """Auto-fix issues and push when everything is clean."""
    force_concise = should_use_concise_mode()
    max_iterations = 3
    iteration = 0

    if not force_concise:
        print(colored_text("🔄 Starting auto-fix and push process...", Colors.BLUE, bold=True))  # noqa: T201

    while iteration < max_iterations:
        iteration += 1
        show_progress(iteration, force_concise)

        # Step 1: Apply ruff formatting
        format_ok, files_formatted = handle_formatting(force_concise)
        if not format_ok:
            return 1

        # Step 2: Apply ruff check fixes
        style_ok, issues_fixed = handle_style_fixes(force_concise)
        if not style_ok:
            return 1

        # Step 3: Check if everything is now clean
        ruff_clean, mypy_clean, tests_clean = run_quality_checks()

        if ruff_clean and mypy_clean and tests_clean:
            return handle_successful_push(force_concise)

        # Step 4: Show remaining issues
        show_remaining_issues(ruff_clean, mypy_clean, tests_clean, force_concise)

        # If no changes were made this iteration, we're stuck
        if files_formatted == 0 and issues_fixed == 0:
            break

    # If we get here, we couldn't auto-fix everything
    show_manual_fix_instructions(force_concise)
    return 1


if __name__ == "__main__":
    sys.exit(auto_fix_and_push())
