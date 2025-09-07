from __future__ import annotations
import asyncio
import logging
import zoneinfo
from typing import Any, Iterable
from types import SimpleNamespace

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .container import build_services

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

def _as_messages(result: Any) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, Iterable) and not isinstance(result, (bytes, bytearray, dict)):
        try:
            items = list(result)
        except Exception:
            return [str(result)]
        return [x if isinstance(x, str) else str(x) for x in items]
    return [str(result)]

async def main() -> None:
    log.info("Building application services...")
    services = build_services()
    app_ctx = SimpleNamespace(
        services=services,
        dispatcher=services.dispatcher,
        agent=services.agent,
        orchestrator=services.orchestrator,
        settings=services.settings,
    )
    
    services.dispatcher.set_app(app_ctx)

    tz = zoneinfo.ZoneInfo(services.settings.TZ)
    sched = AsyncIOScheduler(timezone=tz)

    job_name_map: dict[str, str] = {
        "daily_brief": "daily_brief",
        "dinner_ideas": "dinner",
        "media_digest": "media",
        "entertainment_digest": "entertainment",
        "news_digest": "news",
        "turkish_news_digest": "news_tr",
        "gaming_digest": "gaming",
        "sys_digest": "sys",
        "log_digest": "logs",
    }

    schedule_cfg = getattr(services.settings, "schedule", None)

    if not schedule_cfg:
        log.warning("No schedule configured (settings.schedule is empty). Exiting.")
        try:
            if getattr(services, "http_session", None):
                await services.http_session.close()
        finally:
            return

    raw = schedule_cfg.model_dump() if hasattr(schedule_cfg, "model_dump") else dict(schedule_cfg)

    async def _run_and_notify(job_key: str, **kwargs: Any) -> None:
        log.info("Running job '%s' ...", job_key)
        try:
            result = await services.dispatcher.run(job_key, app=app_ctx, **kwargs)
        except Exception:
            log.exception("Job '%s' failed", job_key)
            return

        messages = _as_messages(result)
        if not messages:
            log.info("Job '%s' produced no output", job_key)
            return

        tg = getattr(services, "telegram_client", None)
        chat_id = getattr(services.settings, "TELEGRAM_CHAT_ID", None)
        for msg in messages:
            if tg and chat_id:
                try:
                    await tg.send_text(chat_id=chat_id, text=msg)
                except Exception:
                    log.exception("Failed to send Telegram notification for job '%s'", job_key)
            else:
                log.info("[NO-TELEGRAM] %s", msg)

    log.info("Registering CRON jobs...")

    for key, entry in raw.items():
        if not isinstance(entry, dict): continue
        if not entry.get("enabled"): continue
        
        cron_expr = entry.get("cron")

        if not cron_expr: continue

        job_key = job_name_map.get(key)

        if not job_key:
            log.warning("No dispatcher job mapped for schedule key '%s' (cron=%r) — skipping", key, cron_expr)
            continue

        try:
            trigger = CronTrigger.from_crontab(cron_expr, timezone=tz)
        except Exception:
            log.exception("Invalid CRON expression for '%s': %r — skipping", key, cron_expr)
            continue

        sched.add_job(_run_and_notify, trigger, name=key, kwargs={"job_key": job_key})
        log.info("Scheduled '%s' (dispatcher job '%s') at CRON %s [%s]", key, job_key, cron_expr, tz.key)

    log.info("Starting scheduler...")
    sched.start()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        log.info("Shutting down scheduler...")
        sched.shutdown(wait=False)
        try:
            if getattr(services, "http_session", None):
                await services.http_session.close()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
