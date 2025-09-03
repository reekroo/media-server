import schedule
import time
import sys
import argparse

from .backup_manager import BackupManager
from .archivers.zipper import Zipper
from .providers.google_cloud import GoogleDriveProvider
from . import backup_logger
from .configs import (
    SCHEDULE_UNIT,
    SCHEDULE_INTERVAL,
    SCHEDULE_DAY,
    SCHEDULE_TIME
)

log = backup_logger.get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Backup Service")
    parser.add_argument(
        '--now',
        action='store_true',
        help="Run one backup cycle immediately and exit."
    )
    args = parser.parse_args()

    log.info("Backup service is starting.")

    try:
        archiver = Zipper()
        provider = GoogleDriveProvider()
        manager = BackupManager(archiver=archiver, provider=provider)

        if args.now:
            log.info("'--now' flag detected. Running a single backup cycle.")
            manager.run_backup()
            log.info("Immediate backup cycle finished. Exiting.")
            sys.exit(0)

        log.info(f"Setting up schedule: every {SCHEDULE_INTERVAL} {SCHEDULE_UNIT} on {SCHEDULE_DAY} at {SCHEDULE_TIME}")

        job = schedule.every(SCHEDULE_INTERVAL)

        if SCHEDULE_UNIT == "weeks":
            day_attr = getattr(job, SCHEDULE_DAY, None)
            if day_attr:
                day_attr.at(SCHEDULE_TIME).do(manager.run_backup)
            else:
                log.error(f"Invalid day of the week in config: {SCHEDULE_DAY}")
                sys.exit(1)
        elif SCHEDULE_UNIT == "days":
             job.days.at(SCHEDULE_TIME).do(manager.run_backup)
        else:
            log.error(f"Time unit '{SCHEDULE_UNIT}' is not supported in the current configuration.")
            sys.exit(1)

        log.info("Service started and waiting for the scheduled time.")
        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        log.critical(f"A critical error occurred during service startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
