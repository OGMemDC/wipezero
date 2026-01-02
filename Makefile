.PHONY: test integration

TEST_PYTHON ?= python3

test:
	$(TEST_PYTHON) -m pytest -q

integration:
	@echo "Integration test is gated: set RUN_INTEGRATION=1 to enable and ensure you're using a disposable runner"
	@if [ "${RUN_INTEGRATION:-0}" = "1" ]; then \
		bash tests/integration_loopback.sh; \
	else \
		echo "Skipping integration; export RUN_INTEGRATION=1 to enable"; \
		exit 0; \
	fi
