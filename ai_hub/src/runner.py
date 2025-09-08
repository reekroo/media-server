from __future__ import annotations

import asyncio
import logging
import zoneinfo
from pathlib import Path
from typing import Any
import tomllib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .app import App
from .container import build_services

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


def _load_schedule(path: Path) -> dict[str, Any]:
    if not path.exists():
        logging.warning("schedule.toml not found at %s", path)
        return {}
    with path.open("rb") as f:
        data = tomllib.load(f)
    return data or {}

def _cron_from_str(expr: str, tz: zoneinfo.ZoneInfo) -> CronTrigger:
    return CronTrigger.from_crontab(expr, timezone=tz)


async def _run_and_notify(app: App, job_key: str) -> None:
    dispatcher = app.services.dispatcher
    log.info("Running job '%s' ...", job_key)
    try:
        chunks = await dispatcher.run(job_key)
    except Exception:
        log.exception("Job '%s' failed", job_key)
        return

    n = len(chunks) if chunks else 0
    log.info("Job '%s' -> %d chunk(s).", job_key, n)
    if not chunks:
        return

    for i, text in enumerate(chunks, 1):
        try:
            log.info(
                "Sending chunk %d/%d for job '%s' (%d chars)...",
                i, n, job_key, len(text) if text else 0
            )
            await app.send_notification(text, send_to="telegram")
        except Exception:
            log.exception("Failed to send chunk %d/%d for job '%s'", i, n, job_key)

async def main() -> None:
    services = build_services()
    app = App(services=services)
    services.dispatcher.set_app(app)

    tz_name = services.settings.TZ or "Europe/Istanbul"
    tz = zoneinfo.ZoneInfo(tz_name)

    repo_root = Path(__file__).resolve().parents[1]
    schedule_file = repo_root / "configs" / "schedule.toml"
    logging.info("Loading schedule from %s", schedule_file)
    data = _load_schedule(schedule_file)

    mapping: dict[str, str] = {
        "daily_brief": "daily_brief",
        "dinner_ideas": "dinner",
        "media_digest": "media",
        "entertainment": "entertainment",
        "news_digest": "news",
        "turkish_news": "news_tr",
        "gaming_digest": "gaming",
        "sys_digest": "sys",
        "log_digest": "logs",
    }

    sched = AsyncIOScheduler(timezone=tz)
    any_job = False
    for section, job_key in mapping.items():
        cfg = data.get(section)
        if not isinstance(cfg, dict):
            continue
        if cfg.get("enabled", True) is False:
            continue
        expr = (cfg.get("cron") or "").strip()
        if not expr:
            logging.warning("Section [%s] enabled but has no 'cron' field", section)
            continue

        try:
            trigger = _cron_from_str(expr, tz)
        except Exception:
            logging.exception(
                "Invalid cron expression in section [%s]: %r", section, expr
            )
            continue

        sched.add_job(
            _run_and_notify,
            trigger,
            args=[app, job_key],
            id=section,
            name=f"{section} ({job_key})",
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60,
        )
        logging.info(
            "Scheduled '%s' (job '%s') at CRON '%s' [%s]",
            section, job_key, expr, tz_name
        )
        any_job = True

    if not any_job:
        logging.warning("schedule.toml not found or empty. No jobs scheduled.")

    sched.start()
    logging.info("Scheduler started. Press Ctrl+C to exit.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler shutting down...")
    finally:
        try:
            sched.shutdown(wait=False)
        except Exception:
            pass
        try:
            await app.close_resources()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
