SHELL := /bin/bash

RFKILL ?= $(shell command -v rfkill 2>/dev/null || echo /usr/sbin/rfkill)
DEVICE ?= bluetooth

.PHONY: help status on off toggle

help:
	@echo "Bluetooth controls:"
	@echo "  make status   - sıaplay status (rfkill list)"
	@echo "  make off      - turn off (rfkill block bluetooth)"
	@echo "  make on       - turn on  (rfkill unblock bluetooth)"
	@echo "  make toggle   - toogle (on/off)"
	@echo ""
	@echo "Vars: RFKILL=$(RFKILL)  DEVICE=$(DEVICE)"
	@echo "Examples: make off | make on | make status | make toggle"

status:
	@$(RFKILL) list 2>/dev/null | awk '1'
	@echo ""
	@echo "Soft blocked: yes -> turn on, no -> turn off"

off:
	@ if [ ! -x "$(RFKILL)" ]; then echo "ERROR: rfkill no found: $(RFKILL)"; exit 1; fi
	@ echo ">> Turn off $(DEVICE) ..."
	@ sudo $(RFKILL) block $(DEVICE) || { echo "rfkill block failed"; exit 1; }
	@ $(MAKE) --no-print-directory status

on:
	@ if [ ! -x "$(RFKILL)" ]; then echo "ERROR: rfkill no found: $(RFKILL)"; exit 1; fi
	@ echo ">> Turn on $(DEVICE) ..."
	@ sudo $(RFKILL) unblock $(DEVICE) || { echo "rfkill unblock failed"; exit 1; }
	@ $(MAKE) --no-print-directory status

toggle:
	@ if [ ! -x "$(RFKILL)" ]; then echo "ERROR: rfkill no found: $(RFKILL)"; exit 1; fi
	@ state="$$( $(RFKILL) list 2>/dev/null | awk '/$(DEVICE)/ {f=1} f && /Soft blocked:/ {print $$3; exit}' )"; \
	if [ "$$state" = "yes" ]; then \
		echo ">> Now: OFF -> Turn on $(DEVICE)"; \
		sudo $(RFKILL) unblock $(DEVICE); \
	else \
		echo ">> Now: ON -> Turn off $(DEVICE)"; \
		sudo $(RFKILL) block $(DEVICE); \
	fi
	@ $(MAKE) --no-print-directory status
