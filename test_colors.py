#!/usr/bin/env python3
"""
Test script to check color support in different terminals.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, ".")

from tests.test_utils import Colors, colored_text, supports_color, safe_emoji_text


def main():
    """Test color output in the current terminal."""
    print("=== COLOR SUPPORT TEST ===")
    print(f"Platform: {sys.platform}")
    print(f"Terminal supports colors: {supports_color()}")
    print(f"TERM: {os.environ.get('TERM', 'Not set')}")
    print(f"MSYSTEM: {os.environ.get('MSYSTEM', 'Not set')}")
    print(f"MINGW_PREFIX: {os.environ.get('MINGW_PREFIX', 'Not set')}")
    print(f"FORCE_COLOR: {os.environ.get('FORCE_COLOR', 'Not set')}")
    print(f"NO_COLOR: {os.environ.get('NO_COLOR', 'Not set')}")
    print()

    # Test colors (using safe_emoji_text to avoid encoding issues)
    print("=== COLOR TESTS ===")
    print(colored_text(safe_emoji_text("✅ This should be GREEN and BOLD", "[PASS] This should be GREEN and BOLD"), Colors.GREEN, bold=True))
    print(colored_text(safe_emoji_text("❌ This should be RED and BOLD", "[FAIL] This should be RED and BOLD"), Colors.RED, bold=True))
    print(colored_text(safe_emoji_text("ℹ️ This should be CYAN", "[INFO] This should be CYAN"), Colors.CYAN))
    print(colored_text(safe_emoji_text("⚠️ This should be YELLOW", "[WARN] This should be YELLOW"), Colors.YELLOW))
    print(colored_text("This should be WHITE", Colors.WHITE))
    print()

    # Raw ANSI test
    print("=== RAW ANSI TEST ===")
    print("\033[92m\033[1mRaw ANSI: GREEN and BOLD\033[0m")
    print("\033[91m\033[1mRaw ANSI: RED and BOLD\033[0m")
    print()

    print("If you see colors above, your terminal supports ANSI colors!")
    print("If not, try running: FORCE_COLOR=1 python test_colors.py")


if __name__ == "__main__":
    main()
