VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
PY        = $(VENV_BIN)/python
APP       = main.py
LOG_FILE ?= ./logs/metrics_exporter.log
PORT     ?= 8001

.PHONY: help
help:
	@echo "Metrics Exporter - manual commands"
	@echo ""
	@echo "  make run-once     # Run exporter in foreground (Ctrl+C to stop)"
	@echo "  make logs         # Show last 200 lines of the rotating log"
	@echo "  make logs-follow  # Follow logs in realtime"
	@echo "  make metrics      # Curl the Prometheus /metrics endpoint"

.PHONY: run-once
run-once:
	@echo ">>> Starting metrics exporter (port $(PORT))"
	@$(PY) $(APP)

.PHONY: logs
logs:
	@echo ">>> Tail $(LOG_FILE)"
	@tail -n 200 $(LOG_FILE) || echo "No log file yet at $(LOG_FILE)"

.PHONY: logs-follow
logs-follow:
	@echo ">>> Follow $(LOG_FILE)"
	@tail -f $(LOG_FILE)

.PHONY: metrics
metrics:
	@echo ">>> GET http://localhost:$(PORT)/metrics"
	@curl -s http://localhost:$(PORT)/metrics | head -n 40
