#!/usr/bin/env python3
"""MyPy wrapper that shows results but doesn't block push."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the original mypy logic
from scripts.run_mypy import run_mypy  # noqa: E402


def run_mypy_warning() -> int:
    """Run mypy but always return success to allow push."""
    # Run the actual mypy check but ignore the return code
    run_mypy()

    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_mypy_warning())
