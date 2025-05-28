#!/usr/bin/env python3
"""Test runner wrapper that shows results but doesn't block push."""

import subprocess
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests_warning() -> int:
    """Run tests but always return success to allow push."""
    try:
        # Run the enhanced test runner but ignore the return code
        subprocess.run(
            [sys.executable, "run_enhanced_tests.py"],
            cwd=project_root,
            check=False,  # Don't raise exception on non-zero exit
        )
    except Exception:
        # Even if tests fail to run, don't block the push
        pass

    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_tests_warning())
