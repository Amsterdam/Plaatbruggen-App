#!/usr/bin/env python3
"""Smart auto-fix and validate script for seamless git push experience."""

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


def run_quality_script(script_name: str, description: str) -> tuple[int, str]:
    """Run one of our quality check scripts and return exit code and output."""
    script_path = project_root / "scripts" / script_name
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
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


def run_enhanced_tests() -> tuple[int, str]:
    """Run our enhanced test suite."""
    try:
        result = subprocess.run(
            [sys.executable, "run_enhanced_tests.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=project_root,
            check=False,
        )
        return result.returncode, (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return 1, f"Error running tests: {e}"


def has_unstaged_changes() -> bool:
    """Check if there are unstaged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            cwd=project_root,
            check=True,
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return bool(result.stdout.strip())


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


def apply_auto_fixes(force_concise: bool) -> tuple[bool, bool]:
    """Apply auto-fixes using our quality scripts. Returns (success, changes_made)."""
    changes_made = False

    # Step 1: Apply ruff formatting (this will auto-format files)
    if not force_concise:
        print(colored_text("🔧 Applying code formatting...", Colors.CYAN))  # noqa: T201

    format_exit, format_output = run_quality_script("run_ruff_format.py", "ruff format")

    # Check if formatting made changes (look for "reformatted" in output)
    if "reformatted" in format_output.lower():
        changes_made = True
        if not force_concise:
            print(colored_text("✅ Code formatting applied", Colors.GREEN))  # noqa: T201

    # Step 2: Apply ruff style fixes (this will auto-fix style issues)
    if not force_concise:
        print(colored_text("🔧 Applying style fixes...", Colors.CYAN))  # noqa: T201

    check_exit, check_output = run_quality_script("run_ruff_check.py", "ruff check")

    # Check if style fixes were made (look for "Fixed" in output)
    if "fixed" in check_output.lower() or "Fixed" in check_output:
        changes_made = True
        if not force_concise:
            print(colored_text("✅ Style fixes applied", Colors.GREEN))  # noqa: T201

    # Both formatting and style fixes should succeed (exit code 0) or be auto-fixable
    # We consider it successful if the scripts ran without major errors
    success = True  # We'll validate quality in the next step

    return success, changes_made


def validate_quality(force_concise: bool) -> tuple[bool, bool, bool]:
    """Run all quality checks and return (ruff_clean, mypy_clean, tests_clean)."""
    if not force_concise:
        print(colored_text("🔍 Validating code quality...", Colors.CYAN))  # noqa: T201

    # Check ruff formatting (should be clean after auto-fixes)
    format_exit, format_output = run_quality_script("run_ruff_format.py", "ruff format check")

    # Check ruff style (should be clean after auto-fixes)
    check_exit, check_output = run_quality_script("run_ruff_check.py", "ruff check")

    # Check mypy (can't be auto-fixed)
    mypy_exit, mypy_output = run_quality_script("run_mypy.py", "mypy")

    # Run tests (can't be auto-fixed)
    test_exit, test_output = run_enhanced_tests()

    # For ruff, we consider it clean if exit code is 0 OR if no unfixable issues remain
    ruff_clean = format_exit == 0 and check_exit == 0
    mypy_clean = mypy_exit == 0
    tests_clean = test_exit == 0

    return ruff_clean, mypy_clean, tests_clean


def commit_auto_fixes(changes_made: bool, force_concise: bool) -> bool:
    """Commit auto-fixes if any were made."""
    if not changes_made:
        return True

    if has_unstaged_changes() and not stage_all_changes():
        if not force_concise:
            print(colored_text("❌ Failed to stage auto-fix changes", Colors.RED))  # noqa: T201
        return False

    commit_msg = "Auto-fix code quality (formatting and style)"
    if commit_changes(commit_msg):
        if not force_concise:
            print(colored_text("✅ Auto-fixes committed", Colors.GREEN))  # noqa: T201
        return True

    if not force_concise:
        print(colored_text("❌ Failed to commit auto-fixes", Colors.RED))  # noqa: T201
    return False


def show_manual_fix_warnings(ruff_clean: bool, mypy_clean: bool, tests_clean: bool, force_concise: bool) -> None:
    """Show warnings for issues that couldn't be auto-fixed."""
    issues = []
    if not ruff_clean:
        issues.append("Code style/formatting")
    if not mypy_clean:
        issues.append("Type checking")
    if not tests_clean:
        issues.append("Tests")

    if not issues:
        return

    if force_concise:
        safe_emoji_text("⚠️ MANUAL FIXES NEEDED", "MANUAL FIXES NEEDED")
        print(f"Issues requiring manual fix: {', '.join(issues)}")  # noqa: T201
    else:
        print(colored_text("⚠️ Some issues require manual fixing:", Colors.YELLOW, bold=True))  # noqa: T201
        print(colored_text(f"Failed checks: {', '.join(issues)}", Colors.YELLOW))  # noqa: T201
        print(colored_text("Please fix these manually and commit the changes:", Colors.CYAN))  # noqa: T201
        if not ruff_clean:
            print(colored_text("  • Run 'python scripts/run_ruff_check.py' for style details", Colors.CYAN))  # noqa: T201
        if not mypy_clean:
            print(colored_text("  • Run 'python scripts/run_mypy.py' for type errors", Colors.CYAN))  # noqa: T201
        if not tests_clean:
            print(colored_text("  • Run 'python run_enhanced_tests.py' for test failures", Colors.CYAN))  # noqa: T201


def report_final_results(ruff_clean: bool, mypy_clean: bool, tests_clean: bool, changes_made: bool, force_concise: bool) -> int:
    """Report final results and return exit code."""
    all_clean = ruff_clean and mypy_clean and tests_clean

    if all_clean:
        if force_concise:
            if changes_made:
                safe_emoji_text("✅ AUTO-FIXED & VALIDATED", "AUTO-FIXED & VALIDATED")
            else:
                safe_emoji_text("✅ ALL CHECKS PASSED", "ALL CHECKS PASSED")
        else:
            safe_emoji_text("🎉 All quality checks passed!", "All quality checks passed!")
            if changes_made:
                print(colored_text("Auto-fixes have been applied and committed.", Colors.GREEN))  # noqa: T201
            print(colored_text("Push will proceed...", Colors.GREEN))  # noqa: T201
        return 0

    # Show warnings for unfixable issues, but don't block push
    show_manual_fix_warnings(ruff_clean, mypy_clean, tests_clean, force_concise)

    if force_concise:
        safe_emoji_text("⚠️ PUSH WITH WARNINGS", "PUSH WITH WARNINGS")
        print("Some issues need manual fixing, but push will continue.")  # noqa: T201
    else:
        print(colored_text("⚠️ Proceeding with warnings...", Colors.YELLOW, bold=True))  # noqa: T201
        print(colored_text("Push will continue, but please address the warnings above.", Colors.YELLOW))  # noqa: T201

    return 0  # Allow push to continue even with warnings


def main() -> int:
    """Main execution function."""
    force_concise = should_use_concise_mode()

    if not force_concise:
        safe_emoji_text("🚀 Smart Auto-Fix and Validate", "Smart Auto-Fix and Validate")
        print(colored_text("Automatically fixing and validating code quality...", Colors.BLUE))  # noqa: T201

    # Step 1: Apply auto-fixes
    fix_success, changes_made = apply_auto_fixes(force_concise)
    if not fix_success:
        if force_concise:
            safe_emoji_text("❌ AUTO-FIX FAILED", "AUTO-FIX FAILED")
        else:
            print(colored_text("❌ Auto-fix process failed", Colors.RED, bold=True))  # noqa: T201
        return 1

    # Step 2: Commit auto-fixes if any were made
    if not commit_auto_fixes(changes_made, force_concise):
        return 1

    # Step 3: Validate final quality
    ruff_clean, mypy_clean, tests_clean = validate_quality(force_concise)

    # Step 4: Report results (warnings only, don't block push)
    return report_final_results(ruff_clean, mypy_clean, tests_clean, changes_made, force_concise)


if __name__ == "__main__":
    sys.exit(main())
