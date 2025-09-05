VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
CLI       = $(VENV_BIN)/weather-monitor
LOG_FILE ?= /home/reekroo/peripheral_scripts/logs/weather_service.log

.PHONY: help
help:
	@echo "Weather Monitor - manual commands"
	@echo ""
	@echo "  make run-once     # Run service in foreground (Ctrl+C to stop)"
	@echo "  make logs         # Show last 200 lines of the rotating log"
	@echo "  make logs-follow  # Follow logs in realtime"

.PHONY: run-once
run-once:
	@echo ">>> Starting weather-monitor"
	@$(CLI)

.PHONY: logs
logs:
	@echo ">>> Tail $(LOG_FILE)"
	@tail -n 200 $(LOG_FILE) || echo "No log file yet at $(LOG_FILE)"

.PHONY: logs-follow
logs-follow:
	@echo ">>> Follow $(LOG_FILE)"
	@tail -f $(LOG_FILE)
