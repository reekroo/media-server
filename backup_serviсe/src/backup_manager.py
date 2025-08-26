import datetime
from pathlib import Path
import os

from .archivers.base import BaseArchiver
from .providers.base import BaseProvider
from . import configs
from . import backup_logger

log = backup_logger.get_logger(__name__)

class BackupManager:

    def __init__(self, archiver: BaseArchiver, provider: BaseProvider):
        self.archiver = archiver
        self.provider = provider
        self.source_dirs = [Path(d) for d in configs.SOURCE_DIRECTORIES]
        self.temp_dir = Path(configs.TEMP_ARCHIVE_PATH)

    def run_backup(self):
        log.info("="*50)
        log.info("Starting a new backup session for all configured directories.")
        
        success_count = 0
        fail_count = 0

        for source_dir in self.source_dirs:
            log.info(f"--- Processing directory: {source_dir} ---")

            if not source_dir.exists():
                log.error(f"Source directory not found: {source_dir}. Skipping.")
                fail_count += 1
                continue

            archive_path = None
            
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                archive_basename = f"backup_{source_dir.name}_{timestamp}"
                destination_path = self.temp_dir / archive_basename

                archive_path = self.archiver.archive(source_dir, destination_path)

                self.provider.upload(archive_path)

                log.info(f"Successfully backed up directory: {source_dir}")
                success_count += 1

            except Exception as e:
                log.error(f"A critical error occurred while backing up {source_dir}: {e}", exc_info=True)
                fail_count += 1

            finally:
                if archive_path and archive_path.exists():
                    try:
                        log.info(f"Deleting temporary archive: {archive_path}")
                        os.remove(archive_path)
                    except OSError as e:
                        log.error(f"Failed to delete temporary archive {archive_path}: {e}")
        
        log.info("Backup session finished.")
        log.info(f"Summary: {success_count} successful, {fail_count} failed.")
        log.info("="*50)
