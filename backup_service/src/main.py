import schedule
import time
import sys
import argparse

from . import configs
from .backup_logger import setup_logger
from .backup_manager import BackupManager
from .archivers.zipper import Zipper
from .providers.google_cloud import GoogleDriveProvider

def main():
    parser = argparse.ArgumentParser(description="Backup Service")
    parser.add_argument('--now', action='store_true', help="Run one backup cycle immediately and exit.")
    args = parser.parse_args()
    
    log = setup_logger(
        "BackupService",
        configs.LOG_FILE_PATH,
        configs.LOG_LEVEL,
        max_bytes=configs.LOG_MAX_BYTES,
        backup_count=configs.LOG_BACKUP_COUNT
    )
    log.info("Backup service is starting.")
    
    try:
        configs.TEMP_ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log.critical(f"Failed to create temp directory: {e}", exc_info=True)
        sys.exit(1)

    try:
        zipper = Zipper(logger=log)
        
        google_provider = GoogleDriveProvider(
            logger=log,
            token_path=configs.TOKEN_FILE_PATH,
            creds_path=configs.CREDENTIALS_FILE_PATH,
            folder_id=configs.GOOGLE_DRIVE_FOLDER_ID,
            scopes=configs.SCOPES
        )
        
        manager = BackupManager(
            archiver=zipper,
            provider=google_provider,
            logger=log,
            source_dirs=configs.SOURCE_DIRECTORIES,
            temp_dir=configs.TEMP_ARCHIVE_PATH
        )

        if args.now:
            log.info("'--now' flag detected. Running a single backup cycle.")
            manager.run_backup()
            log.info("Immediate backup cycle finished. Exiting.")
            sys.exit(0)

        log.info(f"Setting up schedule: every {configs.SCHEDULE_INTERVAL} {configs.SCHEDULE_UNIT} on {configs.SCHEDULE_DAY} at {configs.SCHEDULE_TIME}")

        job = schedule.every(configs.SCHEDULE_INTERVAL)

        if configs.SCHEDULE_UNIT == "weeks":
            day_attr = getattr(job, configs.SCHEDULE_DAY, None)
            if day_attr:
                day_attr.at(configs.SCHEDULE_TIME).do(manager.run_backup)
            else:
                log.error(f"Invalid day of the week in config: {configs.SCHEDULE_DAY}")
                sys.exit(1)
        elif configs.SCHEDULE_UNIT == "days":
             job.days.at(configs.SCHEDULE_TIME).do(manager.run_backup)
        else:
            log.error(f"Time unit '{configs.SCHEDULE_UNIT}' is not supported in the current configuration.")
            sys.exit(1)

        log.info("Service started and waiting for the scheduled time.")
        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        log.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()