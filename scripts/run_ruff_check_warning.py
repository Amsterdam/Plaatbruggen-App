#!/usr/bin/env python3
"""Ruff check wrapper that shows results but doesn't block push."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the original ruff check logic
from scripts.run_ruff_check import run_ruff_check  # noqa: E402


def run_ruff_check_warning() -> int:
    """Run ruff check but always return success to allow push."""
    # Run the actual check but ignore the return code
    run_ruff_check()
    
    # Always return 0 (success) to allow push to continue
    return 0


if __name__ == "__main__":
    sys.exit(run_ruff_check_warning()) 