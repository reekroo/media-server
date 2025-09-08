from __future__ import annotations

import asyncio
import logging
import zoneinfo
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .app import App
from .container import build_services
from .core.scheduling.repo import TomlScheduleRepository
from .core.scheduling.launcher import DispatcherJobLauncher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

def _cron_from_str(expr: str, tz: zoneinfo.ZoneInfo) -> CronTrigger:
    return CronTrigger.from_crontab(expr, timezone=tz)

async def _run_and_notify(app: App, launcher: DispatcherJobLauncher, job_key: str, send_to: str) -> None:
    log.info("Running job '%s' ...", job_key)
    try:
        chunks = await launcher.run(job_key)
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
                "Sending chunk %d/%d for job '%s' (%d chars) via %s...",
                i, n, job_key, len(text) if text else 0, send_to
            )
            await app.send_notification(text, send_to=send_to)
        except Exception:
            log.exception("Failed to send chunk %d/%d for job '%s'", i, n, job_key)

async def main() -> None:
    services = build_services()
    app = App(services=services)
    services.dispatcher.set_app(app)

    tz_name = services.settings.TZ or "Europe/Istanbul"
    tz = zoneinfo.ZoneInfo(tz_name)

    repo_root = Path(__file__).resolve().parents[1]
    schedule_path = repo_root / "configs" / "schedule.toml"

    fallback_mapping = {
        "daily_brief": "daily_brief",
        "news_digest": "news",
        "gaming_digest": "gaming",
        "dinner_ideas": "dinner",
        "media_digest": "media",
        "entertainment": "entertainment",
        "sys_digest": "sys",
        "log_digest": "logs",
        "turkish_news": "news_tr",
    }

    repo = TomlScheduleRepository(schedule_path, fallback_mapping=fallback_mapping)
    jobs = repo.load()

    if not schedule_path.exists():
        log.warning("schedule.toml not found at %s", schedule_path)
    if not jobs:
        log.warning("schedule.toml not found or empty. No jobs scheduled.")

    sched = AsyncIOScheduler(timezone=tz)
    launcher = DispatcherJobLauncher(services.dispatcher)

    any_job = False
    for section, jc in jobs.items():
        if not jc.enabled:
            continue
        try:
            trigger = _cron_from_str(jc.cron, tz)
        except Exception:
            logging.exception("Invalid cron expression in section [%s]: %r", section, jc.cron)
            continue

        sched.add_job(
            _run_and_notify,
            trigger,
            args=[app, launcher, jc.job, jc.to],
            id=section,
            name=f"{section} ({jc.job})",
            coalesce=jc.coalesce,
            max_instances=jc.max_instances,
            misfire_grace_time=jc.misfire_grace_time,
            jitter=jc.jitter,
        )
        logging.info(
            "Scheduled '%s' (job '%s') at CRON '%s' [%s]",
            section, jc.job, jc.cron, tz_name
        )
        any_job = True

    sched.start()
    logging.info("Scheduler started. Press Ctrl+C to exit.")

    if not any_job:
        logging.warning("No enabled jobs to run.")

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
