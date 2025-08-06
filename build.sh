#!/bin/bash

# HiFiBerry DSP Profiles - Build Script
# This script builds the Debian package

set -e  # Exit on any error

echo "Building HiFiBerry DSP Profiles Debian package..."

# Check if we're in the right directory
if [ ! -f "debian/control" ]; then
    echo "Error: debian/control not found. Please run this script from the package root directory."
    exit 1
fi

# Check if required files exist
required_files=(
    "beocreate/beocreate-universal-11.xml"
    "dac+dsp/dacdsp-15.xml"
    "dspaddon/dsp-addon-96-14.xml"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found."
        exit 1
    fi
done

echo "All required files found."

# Clean any previous build artifacts
echo "Cleaning previous build artifacts..."
rm -rf debian/.debhelper debian/hifiberry-dspprofiles debian/tmp debian/*.debhelper* debian/*.substvars 2>/dev/null || true

# Build the package
echo "Building package..."
dpkg-buildpackage -us -uc -b

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Package built successfully!"
    echo ""
    echo "Generated files:"
    ls -la ../hifiberry-dspprofiles_*.deb 2>/dev/null || echo "Package file not found in parent directory"
    echo ""
    echo "To install the package, run:"
    echo "  sudo dpkg -i ../hifiberry-dspprofiles_*.deb"
    echo ""
else
    echo "❌ Package build failed!"
    exit 1
fi
