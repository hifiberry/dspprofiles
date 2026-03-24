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

# Check if DIST is set by environment variable
if [ -n "$DIST" ]; then
    echo "Using distribution from DIST environment variable: $DIST"
    DIST_ARG="--dist=$DIST"
else
    echo "No DIST environment variable set, using sbuild default"
    DIST_ARG=""
fi

# Build the package
echo "Building package with sbuild..."
sbuild --chroot-mode=unshare \
       --no-clean-source \
       --enable-network $DIST_ARG
