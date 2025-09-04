VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
CLI       = $(VENV_BIN)/backup-service
LOG_FILE ?= ./logs/backup_service.log

.PHONY: help
help:
	@echo "Backup Service - manual commands"
	@echo ""
	@echo "  make run-once     # Run one backup cycle immediately (same as --now)"
	@echo "  make logs         # Show last 200 lines of the rotating log file"
	@echo "  make logs-follow  # Follow logs in realtime"

.PHONY: run-once
run-once:
	@echo ">>> Running one backup cycle (--now)"
	@$(CLI) --now

.PHONY: logs
logs:
	@echo ">>> Showing last 200 lines of $(LOG_FILE)"
	@tail -n 200 $(LOG_FILE) || echo "Log file not found: $(LOG_FILE)"

.PHONY: logs-follow
logs-follow:
	@echo ">>> Following $(LOG_FILE)"
	@tail -f $(LOG_FILE)
