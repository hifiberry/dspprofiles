.PHONY: build clean install help

build:
	dpkg-buildpackage -us -uc -b

clean:
	dh_clean || true

install: build
	sudo dpkg -i ../hifiberry-dspprofiles_*.deb

help:
	@echo "Available targets:"
	@echo "  build   - Build the Debian package"
	@echo "  clean   - Clean build artifacts"
	@echo "  install - Install the built package"
	@echo "  help    - Show this help message"

# Empty targets to prevent infinite recursion
configure:
install-data:
