.PHONY: build clean install help

build:
	if [ -n "$$DIST" ]; then \
		echo "Using distribution from DIST environment variable: $$DIST"; \
		DIST_ARG="--dist=$$DIST"; \
		CHROOT_ARG="--chroot=$$CHROOT"; \
	else \
		echo "No DIST environment variable set, using sbuild default"; \
		DIST_ARG=""; \
		CHROOT_ARG=""; \
	fi; \
	sbuild \
		--chroot-mode=unshare \
		--no-clean-source \
		--enable-network \
		$$DIST_ARG \
		$$CHROOT_ARG \
		--verbose

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
