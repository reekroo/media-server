# AI Hub (Docker Edition)

`ai-hub` is a modular AI assistant and automation hub designed to run as a multi-container Docker application.

## Architecture

The system consists of three core services that run in a shared network:
-   **MCP (Master Control Program):** The central JSON-RPC server that acts as the "brain" of the system, executing all core logic.
-   **Runner:** A cron-style scheduler that triggers periodic tasks by making RPC calls to the MCP.
-   **Chat:** The user-facing Telegram bot that receives commands and communicates with the MCP.

## Deployment with Docker

### Prerequisites
* `Docker`
* `Docker Compose`

### Instructions

**1. Prepare Local Directories**
Create the necessary folder structure for your configuration files and persistent state. You will need separate config folders for each environment (e.g., `prod`, `dev`).

```bash
# Create folders for configs (for prod and dev) and a state directory
mkdir -p ./configs/prod ./configs/dev ./state
```
Place all your production `.toml` configuration files (`schedule.toml`, `news.toml`, etc.) into the `./configs/prod` directory. Place your development configs in `./configs/dev`.

**2. Set up the Environment**
Copy the environment template file and fill in your secret keys, tokens, and other environment-specific settings.
```bash
cp .env.prod.template .env.prod
nano .env.prod
```
You must provide `GEMINI_API_KEY`, `GCP_PROJECT_ID`, and `TELEGRAM_BOT_TOKEN`.

**3. Build and Run the Stack**
This single command will build the shared Docker image and start all three services (`mcp`, `runner`, `chat`) in the correct order.
```bash
docker-compose up -d --build
```

**4. Check the Logs**
You can view the combined logs for all services or for a specific one.
```bash
# View logs for all services in the stack
docker-compose logs -f

# View logs for a single service (e.g., the chat bot)
docker-compose logs -f chat
```

**5. Stop the Stack**
To stop all three services, run:
```bash
docker-compose down
```

### Architectural Note: Log Analysis

The functionality defined in `logs.toml` (reading log files from the host filesystem) is an anti-pattern in a containerized environment and will not work with this setup.

**Recommended approach:** All container logs (`stdout`) are already being collected by the `loki/promtail` stack. Log analysis and error detection should be configured in Grafana using LogQL queries and alerts. This centralizes logging and is the standard practice for containerized applications.