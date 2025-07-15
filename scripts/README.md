# F1 Web App Scripts

This directory contains utility scripts for the F1 Web App project.

## Check Distutils Warnings

The `check_distutils_warnings.py` script helps identify potential issues with the deprecated `distutils` module in Python 3.12.

### Background

Python 3.12 has removed the `distutils` module from the standard library. Many packages still rely on `distutils`, which can cause compatibility issues when running with Python 3.12.

### Usage

```bash
# Run the script to check for distutils warnings
python scripts/check_distutils_warnings.py

# Or use it as an executable
./scripts/check_distutils_warnings.py
```

### What it does

1. Runs the application with warnings enabled
2. Captures and filters for any warnings related to `distutils`
3. Checks installed packages for any mentions of `distutils` in their metadata
4. Provides recommendations for addressing any issues found

### Recommendations

If the script identifies packages using `distutils`, you have several options:

1. Update the packages to versions that don't rely on `distutils`
2. Use Python 3.11 instead of 3.12 until all dependencies are updated
3. Add modern packaging dependencies like `setuptools>=68.0.0`, `wheel>=0.41.0`, and `packaging>=23.1` to your requirements

## Other Scripts

Additional utility scripts will be added here as needed.
