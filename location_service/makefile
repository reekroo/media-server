VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
CLI       = $(VENV_BIN)/location-service
LOG_FILE ?= /home/reekroo/peripheral_scripts/logs/location.log

.PHONY: help
help:
	@echo "Location Service - manual commands"
	@echo ""
	@echo "  make run-once    # Run the service in foreground once (without systemd)"
	@echo "  make logs        # Show last 200 lines of logs"
	@echo "  make logs-follow # Follow logs in realtime"

.PHONY: run-once
run-once:
	@echo ">>> Running location-service once"
	@$(CLI)

.PHONY: logs
logs:
	@echo ">>> Showing last 200 lines of $(LOG_FILE)"
	@tail -n 200 $(LOG_FILE) || echo "Log file not found: $(LOG_FILE)"

.PHONY: logs-follow
logs-follow:
	@echo ">>> Following $(LOG_FILE)"
	@tail -f $(LOG_FILE)
