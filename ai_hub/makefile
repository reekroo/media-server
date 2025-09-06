VENV := .venv_ai_hub
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install lint test run-runner run-chat

help:
	@echo "Targets:"
	@echo "  venv        - create venv"
	@echo "  install     - install deps"
	@echo "  run-runner  - start APScheduler jobs"
	@echo "  run-chat    - start Telegram chat bot"
	@echo "  lint/test   - lints & tests"

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -e .

run-runner:
	$(PY) -m src.runner

run-chat:
	$(PY) -m src.channels.telegram_chat.bot

lint:
	@echo "add ruff here"

test:
	@echo "add pytest here"
