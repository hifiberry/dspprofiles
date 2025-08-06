# HiFiBerry DSP Profiles Debian Package

This package contains DSP audio profiles for HiFiBerry sound cards.

## Included Files

- `beocreate-universal-11.xml` - Beocreate Universal profile
- `dacdsp-15.xml` - DAC+DSP profile
- `dsp-addon-96-14.xml` - DSP Add-on profile

## Building the Package

### Prerequisites

Install the required build tools:
```bash
sudo apt-get install debhelper build-essential
```

### Build

To build the Debian package using the provided script:
```bash
./build.sh
```

Or manually:
```bash
dpkg-buildpackage -us -uc -b
```

### Install

To install the package:
```bash
sudo dpkg -i ../hifiberry-dspprofiles_*.deb
```

## Installation Location

The files will be installed to:
```
/usr/share/hifiberry/dspprofiles/
├── beocreate-universal-11.xml
├── dacdsp-15.xml
└── dsp-addon-96-14.xml
```

## Clean Up

To clean build artifacts using the provided script:
```bash
./clean.sh
```

Or manually:
```bash
dh_clean
```
