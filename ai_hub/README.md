# AI Hub

A small, pragmatic orchestrator that runs lightweight “agents” (weather, digests, etc.) and delivers results to channels (Telegram, stdout). It also exposes an optional **MCP (Model Context Protocol) server** via systemd socket activation, so external LLM clients/tools can talk to the hub on‑demand.

---

## TL;DR

- **Run a one‑off task**:
  ```bash
  python -m src.main weather --to telegram
  ```
- **Start the MCP socket** (systemd):
  ```bash
  sudo systemctl enable --now ai-hub-mcp.socket
  ```
- **Configure secrets** in `/etc/default/ai-hub` (see below).

---

## Features

- **Agent-based**: each task (e.g., `weather`) is an agent with a tiny interface (`run()` → `Message`).
- **Pluggable providers**: add LLMs / APIs (e.g., Gemini) behind a simple `Provider` base class.
- **Multiple channels**: send output to Telegram or print to stdout.
- **Socket-activated MCP server**: launches only on first connection; no idle cost.
- **Clean logging & predictable paths**: explicit runtime dirs under `/run/ai-hub` and data under `/var/lib/ai-hub`.
- **Single‑file env config**: `/etc/default/ai-hub` for secrets (keys/tokens/IDs).

---

## Architecture

```
CLI → App → Container → Agent → Provider(s) → Channel(s)
                               ╰─→ (optional) MCP Server ← systemd socket
```

- **App (`src/app.py`)** — orchestrates: parses args, builds agent, runs it, ships the message to the chosen channel.
- **Container (`src/container.py`)** — wiring/DI: knows how to build agents, providers and channels.
- **Agents (`src/core/agents/…`)** — implement domain logic, e.g. `WeatherAgent`.
- **Providers (`src/core/providers/…`)** — external services, e.g. `GeminiProvider`.
- **Channels (`src/core/channels/…`)** — delivery, e.g. `TelegramChannel`, `StdoutChannel`.
- **MCP (`mcp/…`)** — a sibling package to `src/` providing a socket‑activated server.

### Typical flow
1. You run: `python -m src.main weather --to telegram`.
2. `App` asks `Container` to **build the agent** and the **channel**.
3. Agent gathers the data (optionally calls providers), returns a rendered `Message`.
4. Channel delivers it (sends to Telegram or prints to stdout).

---

## Directory layout

```
ai_hub/
├─ src/
│  ├─ main.py
│  ├─ app.py
│  ├─ container.py
│  ├─ core/
│  │  ├─ agents/
│  │  │  ├─ __init__.py
│  │  │  ├─ factory.py            # def build_agent(name: str, settings) -> Agent
│  │  │  ├─ base.py               # Agent protocol / ABC
│  │  │  └─ weather.py            # Example agent
│  │  ├─ channels/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py               # Channel ABC
│  │  │  ├─ stdout.py
│  │  │  └─ telegram.py
│  │  ├─ providers/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py               # Provider ABC
│  │  │  └─ gemini.py             # Gemini integration
│  │  └─ utils/
│  │     ├─ logger.py
│  │     └─ settings.py           # loads env, default paths
│  └─ …
├─ mcp/                           # ← sibling to src (not inside)
│  ├─ __init__.py
│  ├─ server.py                   # socket-activated MCP server entrypoint
│  └─ routes/
│     └─ health.py
├─ tests/
├─ pyproject.toml
├─ Makefile
└─ README.md
```

> We intentionally keep **`mcp/` next to `src/`** (as planned earlier), not nested under it.

---

## Requirements

- Python **3.11+**
- Raspberry Pi OS / Debian‑based Linux with **systemd**
- Optional: outbound internet for Gemini / Telegram

---

## Installation

### 1) Clone & venv
```bash
cd ~/ai_hub
python3 -m venv .venv_ai_hub
source .venv_ai_hub/bin/activate
python -m pip install -U pip
pip install -e .
```

### 2) Runtime & data dirs
We use explicit paths (override via env if needed):
- Runtime (sockets/tmp): **`/run/ai-hub`**
- Persistent data: **`/var/lib/ai-hub`**

Create them and (optionally) a dedicated user:
```bash
sudo useradd --system --home /var/lib/ai-hub --shell /usr/sbin/nologin aihub || true
sudo mkdir -p /run/ai-hub /var/lib/ai-hub
sudo chown -R aihub:aihub /run/ai-hub /var/lib/ai-hub
```

To auto‑create `/run/ai-hub` on boot, use tmpfiles:
```bash
sudo tee /etc/tmpfiles.d/ai-hub.conf >/dev/null <<'EOF'
d /run/ai-hub 0755 aihub aihub -
EOF
sudo systemd-tmpfiles --create /etc/tmpfiles.d/ai-hub.conf
```

### 3) Secrets & settings
Place **all secrets and settings** in `/etc/default/ai-hub`:
```bash
sudo tee /etc/default/ai-hub >/dev/null <<'EOF'
# === AI Hub settings ===
# Required for LLM provider(s)
GEMINI_API_KEY=YOUR_GEMINI_KEY

# Telegram delivery (channel)
TELEGRAM_BOT_TOKEN=YOUR_TG_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_DEFAULT_CHAT_ID   # default recipient for digests

# Runtime paths (optional overrides)
AI_HUB_RUN_DIR=/run/ai-hub
AI_HUB_DATA_DIR=/var/lib/ai-hub
AI_HUB_LOG_LEVEL=INFO
EOF
```
> Keep this file out of git.

---

## Usage (CLI)

Run agents via the module entrypoint:
```bash
# Print to stdout
python -m src.main weather --to stdout

# Send to Telegram
python -m src.main weather --to telegram
```

Common flags:
- `--to {telegram,stdout}` – delivery channel
- `--agent <name>` – override agent name (advanced)
- `--dry-run` – compute but do not deliver (still logs)
- `--verbose` – more logging

### Message format
Agents return a `Message` object with:
- `title` (optional)
- `text` (plain text / Markdown for Telegram)
- `attachments` (optional, e.g., images later)

---

## MCP server (socket activation)

We run the MCP server **on demand** via systemd **socket activation**. The socket listens at `/run/ai-hub/mcp.sock` and systemd spawns the service on first connection.

### Unit files

**`/etc/systemd/system/ai-hub-mcp.socket`**
```ini
[Unit]
Description=AI Hub MCP Socket

[Socket]
ListenStream=/run/ai-hub/mcp.sock
SocketUser=aihub
SocketGroup=aihub
SocketMode=0660
RemoveOnStop=true

[Install]
WantedBy=sockets.target
```

**`/etc/systemd/system/ai-hub-mcp.service`**
```ini
[Unit]
Description=AI Hub MCP Server
After=network-online.target
Requires=ai-hub-mcp.socket

[Service]
Type=simple
User=aihub
Group=aihub
EnvironmentFile=/etc/default/ai-hub
WorkingDirectory=/home/reekroo/ai_hub
ExecStart=/home/reekroo/ai_hub/.venv_ai_hub/bin/python -m mcp.server --socket /run/ai-hub/mcp.sock
Restart=on-failure
RestartSec=2s

[Install]
WantedBy=multi-user.target
```

### Manage
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ai-hub-mcp.socket

# Check status
systemctl status ai-hub-mcp.socket
journalctl -u ai-hub-mcp.service -f
```

---

## Configuration reference (env)

| Variable | Required | Default | Purpose |
|---|:---:|---|---|
| `GEMINI_API_KEY` | ✓ | – | LLM provider key |
| `TELEGRAM_BOT_TOKEN` | ✓ (if using Telegram) | – | Telegram bot token |
| `TELEGRAM_CHAT_ID` | ✓ (if using Telegram) | – | Default chat/channel (numeric) |
| `AI_HUB_RUN_DIR` |  | `/run/ai-hub` | Runtime dir (sockets/tmp) |
| `AI_HUB_DATA_DIR` |  | `/var/lib/ai-hub` | Persistent state |
| `AI_HUB_LOG_LEVEL` |  | `INFO` | Logging level |

---

## Adding a new Agent (example)

1. Create `src/core/agents/myagent.py`:
   ```python
   from .base import Agent

   class MyAgent(Agent):
       name = "myagent"

       def __init__(self, providers, settings, log):
           self.providers = providers
           self.settings = settings
           self.log = log

       def run(self):
           # collect data and render string
           text = "Hello from MyAgent"
           return {"title": "MyAgent", "text": text}
   ```
2. Register in `src/core/agents/factory.py`:
   ```python
   from .weather import WeatherAgent
   from .myagent import MyAgent

   def build_agent(name, providers, settings, log):
       table = {
           "weather": WeatherAgent,
           "myagent": MyAgent,
       }
       cls = table.get(name)
       if not cls:
           raise ValueError(f"Unknown agent: {name}")
       return cls(providers=providers, settings=settings, log=log)
   ```
3. Run:
   ```bash
   python -m src.main myagent --to stdout
   ```

> Agents should avoid heavy init; build providers lazily only if needed.

---

## Telegram quickstart

- Create a bot via **@BotFather** → obtain `TELEGRAM_BOT_TOKEN`.
- Add the bot to your chat/channel and send a message.
- Obtain `TELEGRAM_CHAT_ID` (e.g., by calling `getUpdates` on the Bot API after sending a message, or using a helper bot). Use the numeric ID.

**Formatting**: Telegram supports Markdown/HTML (v2 for advanced). Keep content simple; escape special characters when needed.

---

## Gemini quickstart

- Create an API key in **Google AI Studio** (Gemini).
- Paste it into `/etc/default/ai-hub` as `GEMINI_API_KEY`.
- Provider code lives in `src/core/providers/gemini.py`.

> Network access must be available from the device for provider calls.

---

## Logging

- Controlled by `AI_HUB_LOG_LEVEL` (default `INFO`).
- Journald for systemd units; otherwise logs to stdout.
- Typical check:
  ```bash
  journalctl -u ai-hub-mcp.service -n 200 --no-pager
  ```

---


## Troubleshooting

### `ImportError: cannot import name 'build_agent' from 'src.core.agents.factory'`
- Ensure `src/core/agents/factory.py` **defines** `build_agent(...)` and that the package has `__init__.py` files.
- Run from the **project root**:
  ```bash
  python -m src.main weather --to telegram
  ```
  (Don’t run `python src/main.py` — module mode sets `PYTHONPATH` correctly.)

### MCP socket is inactive
- Enable the socket unit (not just the service):
  ```bash
  sudo systemctl enable --now ai-hub-mcp.socket
  systemctl status ai-hub-mcp.socket
  ```
- Verify runtime dir exists and permissions allow `aihub` to create the socket.

### Telegram message not delivered
- Double‑check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Make sure the bot is **added to the chat** and you sent at least one message there.

### No provider output (Gemini)
- Verify `GEMINI_API_KEY` is set and the device has internet access.
- Check provider logs at `DEBUG` level.

---

## Roadmap / Ideas
- More agents (earthquakes, daily digest, system health summary).
- Attachments (charts/images) for richer Telegram posts.
- Configurable schedules (cron/systemd timers) for recurring digests.
- Pluggable authentication for the MCP server if exposed beyond local use.
