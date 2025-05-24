#!/usr/bin/env python3
"""Test script to check pre-commit color behavior."""

import os
import subprocess
import sys
from pathlib import Path

def test_color_settings():
    """Test different color environment variables."""
    
    print("Testing pre-commit color settings...\n")
    
    # Test cases
    test_cases = [
        ("Default", {}),
        ("FORCE_COLOR=1", {"FORCE_COLOR": "1"}),
        ("PRE_COMMIT_COLOR=always", {"PRE_COMMIT_COLOR": "always"}),
        ("PRE_COMMIT_COLOR=auto", {"PRE_COMMIT_COLOR": "auto"}),
        ("Both FORCE_COLOR and PRE_COMMIT_COLOR", {"FORCE_COLOR": "1", "PRE_COMMIT_COLOR": "always"}),
        ("TERM=xterm-256color", {"TERM": "xterm-256color"}),
        ("COLORTERM=truecolor", {"COLORTERM": "truecolor"}),
    ]
    
    for name, env_vars in test_cases:
        print(f"=== {name} ===")
        
        # Set environment variables
        env = os.environ.copy()
        env.update(env_vars)
        
        # Show what we're setting
        if env_vars:
            env_str = ", ".join([f"{k}={v}" for k, v in env_vars.items()])
            print(f"Environment: {env_str}")
        else:
            print("Environment: Default")
        
        # Test with a simple pre-commit run
        try:
            result = subprocess.run(
                ["pre-commit", "run", "--color", "always", "ruff-check"],
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            # Show the output (first few lines)
            if result.stdout:
                lines = result.stdout.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"OUT: {line}")
            
            if result.stderr:
                lines = result.stderr.split('\n')[:3]
                for line in lines:
                    if line.strip():
                        print(f"ERR: {line}")
                        
        except subprocess.TimeoutExpired:
            print("Timed out")
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_color_settings() 