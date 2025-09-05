VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
CLI       = $(VENV_BIN)/earthquake-monitor
PY        = $(VENV_BIN)/python
LOG_FILE ?= /home/reekroo/peripheral_scripts/logs/earthquake_monitor.log

.PHONY: help
help:
	@echo "Earthquake Monitor - manual commands"
	@echo ""
	@echo "  make run-once       	# Run service in foreground (Ctrl+C to stop)"
	@echo "  make logs           	# Show last 200 lines of the rotating log"
	@echo "  make logs-follow    	# Follow logs in realtime"
	@echo "  make alert-test     	# Trigger a 5-second buzzer test (integration test)"
	@echo "  make test           	# Run all unit tests"

.PHONY: run-once
run-once:
	@echo ">>> Starting earthquake-monitor"
	@$(CLI)

.PHONY: logs
logs:
	@echo ">>> Tail $(LOG_FILE)"
	@tail -n 200 $(LOG_FILE) || echo "No log file yet at $(LOG_FILE)"

.PHONY: logs-follow
logs-follow:
	@echo ">>> Follow $(LOG_FILE)"
	@tail -f $(LOG_FILE)

.PHONY: alert-test
alert-test:
	@echo ">>> Running physical alert test (5 seconds)"
	@$(PY) tests/integration_test_alert.py

.PHONY: test
test:
	@echo ">>> Running all tests"
	@$(PY) -m pytest -v