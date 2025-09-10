import asyncio
import logging
import tomllib
import jsonrpc_async
import zoneinfo
from pathlib import Path
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# --- Настройка ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("Runner")

MCP_HOST = "127.0.0.1"
MCP_PORT = 8484

# --- RPC Клиент для связи с MCP ---
async def call_mcp(method: str, params: Dict[str, Any]) -> None:
    """Подключается к MCP и вызывает RPC-метод."""
    log.info(f"Triggering MCP method '{method}' with params: {params}")
    try:
        client = jsonrpc_async.Client(f"tcp://{MCP_HOST}:{MCP_PORT}")
        result = await client.call(method, **params)
        log.info(f"MCP method '{method}' executed successfully. Result: {result}")
    except Exception as e:
        log.error(f"Failed to call MCP method '{method}'. Error: {e}", exc_info=True)

# --- Основная логика ---
async def main() -> None:
    # 1. Настройка временной зоны
    # (Предполагаем, что TZ есть в .env или берется дефолтное значение)
    from src.core.settings import Settings
    settings = Settings()
    tz = zoneinfo.ZoneInfo(settings.TZ)
    log.info(f"Scheduler timezone set to: {tz}")

    # 2. Загрузка расписания
    schedule_path = settings.BASE_DIR / "configs" / "schedule.toml"
    if not schedule_path.exists():
        log.error(f"schedule.toml not found at {schedule_path}. Exiting.")
        return

    schedule_data = tomllib.loads(schedule_path.read_text("utf-8"))

    # 3. Инициализация планировщика
    scheduler = AsyncIOScheduler(timezone=tz)
    
    # 4. Добавление задач в планировщик
    job_count = 0
    for job_id, config in schedule_data.items():
        if not config.get("enabled", False):
            continue

        cron_expr = config.get("cron")
        rpc_method = config.get("rpc_method")
        params = config.get("params", {})

        if not cron_expr or not rpc_method:
            log.warning(f"Skipping job '{job_id}': missing 'cron' or 'rpc_method'.")
            continue

        try:
            scheduler.add_job(
                call_mcp,
                trigger=CronTrigger.from_crontab(cron_expr, timezone=tz),
                id=job_id,
                name=job_id,
                kwargs={"method": rpc_method, "params": params},
                coalesce=True,
                max_instances=1,
            )
            log.info(f"Scheduled job '{job_id}': CRON='{cron_expr}', Method='{rpc_method}'")
            job_count += 1
        except Exception as e:
            log.error(f"Failed to schedule job '{job_id}'. Error: {e}")

    if job_count == 0:
        log.warning("No jobs were scheduled. Check your schedule.toml.")
        return

    # 5. Запуск планировщика
    scheduler.start()
    print(f"✅ Runner started with {job_count} scheduled job(s). Press Ctrl+C to exit.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        log.info("Runner shutting down...")
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())