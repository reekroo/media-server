import asyncio
import json
import logging
import tomllib
import zoneinfo
from pathlib import Path
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.settings import Settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("Runner")

MCP_HOST = "127.0.0.1"
MCP_PORT = 8484

async def call_mcp(method: str, params: Dict[str, Any]) -> None:
    """Подключается к MCP, отправляет одну команду и отключается."""
    log.info(f"Triggering MCP method '{method}' with params: {params}")
    try:
        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ: Используем стандартный asyncio клиент ---
        reader, writer = await asyncio.open_connection(MCP_HOST, MCP_PORT)

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1, # ID может быть любым для runner
        }
        
        writer.write((json.dumps(request) + '\n').encode())
        await writer.drain()

        # Опционально: можно дождаться ответа от MCP
        # response_raw = await reader.readline()
        # log.info(f"MCP response: {response_raw.decode()}")

        writer.close()
        await writer.wait_closed()
        log.info(f"MCP method '{method}' executed successfully.")
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
    except Exception as e:
        log.error(f"Failed to call MCP method '{method}'. Error: {e}", exc_info=True)

async def main() -> None:
    # ... (остальной код main остается без изменений)
    settings = Settings()
    tz = zoneinfo.ZoneInfo(settings.TZ)
    schedule_path = settings.BASE_DIR / "configs" / "schedule.toml"
    schedule_data = tomllib.loads(schedule_path.read_text("utf-8"))
    scheduler = AsyncIOScheduler(timezone=tz)
    
    # ... (цикл добавления задач остается без изменений)
    for job_id, config in schedule_data.items():
        if not config.get("enabled", False): continue
        cron_expr = config.get("cron")
        rpc_method = config.get("rpc_method")
        params = config.get("params", {})
        if not cron_expr or not rpc_method: continue
        scheduler.add_job(call_mcp, CronTrigger.from_crontab(cron_expr, timezone=tz),
                          id=job_id, name=job_id,
                          kwargs={"method": rpc_method, "params": params},
                          coalesce=True, max_instances=1)
        log.info(f"Scheduled job '{job_id}': CRON='{cron_expr}', Method='{rpc_method}'")

    scheduler.start()
    print(f"✅ Runner started with {len(scheduler.get_jobs())} scheduled job(s). Press Ctrl+C to exit.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Runner shutting down...")