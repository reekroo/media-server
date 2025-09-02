VENV_BIN ?= /home/reekroo/peripheral_scripts/.venv_peripherals/bin
CLI      ?= $(VENV_BIN)/network-policy-apply

LAN_IF   ?= eth0
PERIPHERALS_ROOT ?= /home/reekroo/peripheral_scripts
LOG_FILE ?= $(PERIPHERALS_ROOT)/logs/network_policy.log

SUDO ?= sudo

IP     ?= ip
RFKILL ?= rfkill
GREP   ?= grep
AWK    ?= awk
TAIL   ?= tail
JCTL   ?= journalctl

.PHONY: help
help:
	@echo "Network Policy — manual controls"
	@echo ""
	@echo "  make wifi-status        # dısplay status Wi-Fi (rfkill)"
	@echo "  make lan-status         # dısplay status LAN ($(LAN_IF))"
	@echo "  make wifi-block         # block Wi-Fi (rfkill block)"
	@echo "  make wifi-unblock       # unblock Wi-Fi (rfkill unblock)"
	@echo "  make wifi-toggle        # toogle Wi-Fi"
	@echo "  make apply              # run policy once (network-policy-apply)"
	@echo "  make dry-run            # emulate policy base oı current LAN state"
	@echo "  make logs               # last lınes of policy log"
	@echo "  make logs-follow        # follow systemd logs"
	@echo "  make env                # env policy propertıes"
	@echo "  make check              # check required binaries"

# ====== Status ======
.PHONY: wifi-status
wifi-status:
	@echo ">>> Wi-Fi rfkill state:"
	@$(SUDO) $(RFKILL) list wifi || true

.PHONY: lan-status
lan-status:
	@echo ">>> LAN ($(LAN_IF)) link state:"
	@$(IP) -o link show $(LAN_IF) || (echo "Interface $(LAN_IF) not found"; exit 1)
	@$(IP) addr show $(LAN_IF) | sed 's/^\s\+//'

# ====== Controls ======
.PHONY: wifi-block
wifi-block:
	@echo ">>> rfkill block wifi"
	@$(SUDO) $(RFKILL) block wifi
	@$(MAKE) wifi-status

.PHONY: wifi-unblock
wifi-unblock:
	@echo ">>> rfkill unblock wifi"
	@$(SUDO) $(RFKILL) unblock wifi
	@$(MAKE) wifi-status

.PHONY: wifi-toggle
wifi-toggle:
	@state=`$(SUDO) $(RFKILL) list wifi 2>/dev/null | $(GREP) -i "Soft blocked" | $(AWK) '{print $$3}'`; \
	if [ "$$state" = "yes" ]; then \
	  echo ">>> Wi-Fi is soft-blocked → UNBLOCK"; \
	  $(SUDO) $(RFKILL) unblock wifi; \
	else \
	  echo ">>> Wi-Fi is not soft-blocked → BLOCK"; \
	  $(SUDO) $(RFKILL) block wifi; \
	fi; \
	$(MAKE) -s wifi-status

# ====== Policy runner ======
.PHONY: apply
apply:

.PHONY: dry-run
dry-run:
	@up=`$(IP) -o link show $(LAN_IF) 2>/dev/null | $(GREP) -c "state UP" || true`; \
	if [ "$$up" = "1" ]; then \
	  echo "LAN $(LAN_IF): UP  → policy would BLOCK Wi-Fi"; \
	else \
	  echo "LAN $(LAN_IF): DOWN → policy may UNBLOCK Wi-Fi (if AUTO_UNBLOCK_WHEN_LAN_DOWN=1)"; \
	fi

# ====== Logs ======
.PHONY: logs
logs:

UNIT ?= network-policy.service
.PHONY: logs-follow
logs-follow:
	@echo ">>> journalctl -u $(UNIT) -f"
	@$(SUDO) $(JCTL) -u $(UNIT) -f

# ====== Env & Checks ======
.PHONY: env
env:
	@echo "PERIPHERALS_ROOT=$(PERIPHERALS_ROOT)"
	@echo "LAN_INTERFACE=$(LAN_IF)"
	@echo "LOG_FILE=$(LOG_FILE)"
	@echo "CLI=$(CLI)"
	@echo "VENV_BIN=$(VENV_BIN)"

.PHONY: check
check:
	@ok=1; \
	for b in "$(IP)" "$(RFKILL)" "$(CLI)"; do \
	  if ! command -v $$b >/dev/null 2>&1; then \
	    echo "Missing binary: $$b"; ok=0; \
	  fi; \
	done; \
	if [ "$$ok" = "1" ]; then echo "All required binaries are present."; else exit 1; fi
