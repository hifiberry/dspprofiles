#!/bin/bash

# HiFiBerry DSP Profiles - Clean Script
# This script cleans all build artifacts

set -e  # Exit on any error

echo "Cleaning HiFiBerry DSP Profiles build artifacts..."

# Check if we're in the right directory
if [ ! -f "debian/control" ]; then
    echo "Error: debian/control not found. Please run this script from the package root directory."
    exit 1
fi

# Clean debian build artifacts
echo "Removing debian build artifacts..."
rm -rf debian/.debhelper debian/hifiberry-dspprofiles debian/tmp debian/*.debhelper* debian/*.substvars 2>/dev/null || true

# Clean generated package files in parent directory
echo "Removing generated package files..."
rm -f ../hifiberry-dspprofiles_*.deb ../hifiberry-dspprofiles_*.buildinfo ../hifiberry-dspprofiles_*.changes 2>/dev/null || true

# Run debhelper clean if available
if command -v dh_clean >/dev/null 2>&1; then
    echo "Running dh_clean..."
    dh_clean 2>/dev/null || true
fi

echo "✅ Clean completed successfully!"
echo ""
echo "All build artifacts have been removed."
