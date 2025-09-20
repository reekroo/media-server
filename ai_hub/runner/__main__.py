import asyncio
import tomllib
import zoneinfo
from typing import Dict, Any, List
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.settings import Settings
from core.logging import setup_logger, LOG_FILE_PATH

from .rpc_client import RpcClient

log = setup_logger(__name__, LOG_FILE_PATH)

def _normalize_cron_list(value: Any) -> List[str]:
    if isinstance(value, str):
        s = value.strip()
        if not s: raise ValueError("cron string is empty")
        return [s]
    
    if isinstance(value, list):
        items = [str(x).strip() for x in value if str(x).strip()]
        if not items: raise ValueError("cron list is empty after normalization")
        return items
    
    raise ValueError(f"cron must be string or list of strings, got {type(value).__name__}")

async def _job_wrapper(client: RpcClient, method: str, params: Dict[str, Any]) -> None:
    log.info(f"Triggering MCP method '%s' with params: %s", method, params)
    try:
        response = await client.call(method, **params)
        if response.get("ok"):
            log.info("MCP method '%s' completed successfully.", method)
        else:
            error_info = response.get('error', {'message': 'unknown error'})
            log.error("MCP method '%s' returned an error: %s", method, error_info)

    except Exception as e:
        log.error("Failed to call MCP method '%s'. Transport Error: %s", method, e, exc_info=True)

async def main() -> None:
    settings = Settings()
    rpc_client = RpcClient(settings)
    
    tz = zoneinfo.ZoneInfo(settings.TZ)
    log.info(f"Scheduler timezone set to: {tz}")

    schedule_path = settings.BASE_DIR / "configs" / "schedule.toml"
    if not schedule_path.exists():
        log.error(f"schedule.toml not found at {schedule_path}. Exiting.")
        return

    schedule_data = tomllib.loads(schedule_path.read_text("utf-8"))
    scheduler = AsyncIOScheduler(timezone=tz)

    job_count = 0
    for job_id, config in schedule_data.items():
        if not isinstance(config, dict): continue
        if not config.get("enabled", False): continue
        rpc_method = config.get("rpc_method")
        params = config.get("params", {}) or {}
        cron_raw = config.get("cron")
        if not cron_raw or not rpc_method: continue
        try:
            cron_list = _normalize_cron_list(cron_raw)
        except Exception as e:
            log.error(f"Failed to read 'cron' for job '{job_id}': {e}")
            continue

        for idx, cron_expr in enumerate(cron_list, start=1):
            try:
                job_name = f"{job_id}#{idx}" if len(cron_list) > 1 else job_id
                
                job_func = partial(_job_wrapper, client=rpc_client, method=rpc_method, params=params)
                
                scheduler.add_job(
                    job_func,
                    trigger=CronTrigger.from_crontab(cron_expr, timezone=tz),
                    id=job_name, name=job_name,
                    coalesce=True, max_instances=1,
                )
                log.info(f"Scheduled job '{job_name}': CRON='{cron_expr}', Method='{rpc_method}'")
                job_count += 1
            except Exception as e:
                log.error(f"Failed to schedule job '{job_id}' (expr '{cron_expr}'). Error: {e}")

    if job_count == 0:
        log.warning("No jobs were scheduled. Check your schedule.toml.")
        return

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