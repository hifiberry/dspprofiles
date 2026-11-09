.PHONY: build clean install help

# Same build as the build host's: sbuild in a clean chroot, DIST from the
# environment. build.sh is the one place that defines it.
build:
	./build.sh

clean:
	dh_clean || true

install: build
	sudo dpkg -i ../hifiberry-dspprofiles_*.deb

help:
	@echo "Available targets:"
	@echo "  build   - Build the Debian package with sbuild (runs build.sh)"
	@echo "  clean   - Clean build artifacts"
	@echo "  install - Install the built package"
	@echo "  help    - Show this help message"

# Empty targets to prevent infinite recursion
configure:
install-data:
