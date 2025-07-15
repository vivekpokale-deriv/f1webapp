#!/usr/bin/env python3
"""
Script to check for distutils deprecation warnings in Python 3.12.

This script runs the application with warnings enabled and filters for
any warnings related to distutils. This helps identify packages that
might still be using the deprecated distutils module.

Usage:
    python scripts/check_distutils_warnings.py

The script will run the application and print any distutils-related warnings.
"""

import os
import sys
import warnings
import subprocess
import re

# Enable all warnings
warnings.filterwarnings("always")

def check_for_distutils_warnings():
    """Run the application and check for distutils warnings."""
    print("Checking for distutils deprecation warnings...")
    
    # Run the application with warnings enabled
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "always"
    
    # Use subprocess to capture stderr where warnings are printed
    result = subprocess.run(
        [sys.executable, "run.py"],
        env=env,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10  # Timeout after 10 seconds
    )
    
    # Filter for distutils warnings
    distutils_warnings = []
    for line in result.stderr.splitlines():
        if "distutils" in line.lower():
            distutils_warnings.append(line)
    
    if distutils_warnings:
        print("\nFound distutils warnings:")
        for warning in distutils_warnings:
            print(f"  - {warning}")
        
        print("\nRecommendations:")
        print("  1. Update the packages that are generating these warnings")
        print("  2. If you can't update the packages, consider using Python 3.11 instead of 3.12")
        print("  3. Check if newer versions of these packages are available that don't use distutils")
    else:
        print("No distutils warnings found. Your application should be compatible with Python 3.12.")

def check_installed_packages():
    """Check installed packages for distutils dependencies."""
    print("\nChecking installed packages for distutils dependencies...")
    
    # Run pip show for each package and look for distutils
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    packages = []
    for line in result.stdout.splitlines()[2:]:  # Skip header lines
        match = re.match(r"(\S+)\s+(\S+)", line)
        if match:
            packages.append(match.group(1))
    
    distutils_packages = []
    for package in packages:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            stdout=subprocess.PIPE,
            text=True
        )
        if "distutils" in result.stdout.lower():
            distutils_packages.append(package)
    
    if distutils_packages:
        print("\nPackages that might use distutils:")
        for package in distutils_packages:
            print(f"  - {package}")
    else:
        print("No packages found that explicitly mention distutils.")

if __name__ == "__main__":
    check_for_distutils_warnings()
    check_installed_packages()
