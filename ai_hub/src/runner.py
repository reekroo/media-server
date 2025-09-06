import asyncio
import zoneinfo
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .app import App

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    app = App()
    tz = zoneinfo.ZoneInfo(app.settings.TZ)
    sched = AsyncIOScheduler(timezone=tz)

    async def daily_brief_job():
        logging.info("Running daily brief job...")
        message = await app.run_daily_brief()
        await app.send_notification(message)

    async def media_digest_job():
        logging.info("Running media digest job...")
        message = await app.run_media_digest()
        await app.send_notification(message)

    async def sys_digest_job():
        logging.info("Running system digest job...")
        message = await app.run_sys_digest()
        await app.send_notification(message)

    async def news_digest_job():
        logging.info("Running news digest job...")
        messages = await app.run_news_digest()
        for msg in messages:
            await app.send_notification(msg)
            await asyncio.sleep(1)

    async def gaming_digest_job():
        logging.info("Running gaming digest job...")
        messages = await app.run_gaming_digest()
        for msg in messages:
            await app.send_notification(msg)

    job_map = {
        "daily_brief": daily_brief_job,
        "media_digest": media_digest_job,
        "sys_digest": sys_digest_job,
        "news_digest": news_digest_job,
        "gaming_digest": gaming_digest_job,
    }

    if app.settings.schedule:
        for job_name, schedule_entry in app.settings.schedule.model_dump().items():
            if schedule_entry and schedule_entry.get("enabled", False):
                job_func = job_map.get(job_name)
                if job_func:
                    cron_str = schedule_entry["cron"]
                    sched.add_job(
                        job_func,
                        CronTrigger.from_crontab(cron_str, timezone=tz),
                        id=job_name,
                        coalesce=True,
                        misfire_grace_time=600
                    )
                    logging.info(f"Scheduled job '{job_name}' with cron: '{cron_str}'")
                else:
                    logging.warning(f"Job '{job_name}' is configured in schedule.toml but has no matching function.")
    else:
        logging.warning("schedule.toml not found or empty. No jobs scheduled.")
    

    sched.start()
    logging.info("Scheduler started. Press Ctrl+C to exit.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler shutting down...")
    finally:
        sched.shutdown(wait=False)
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())