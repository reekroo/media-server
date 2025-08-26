import shutil
from pathlib import Path
from .base import BaseArchiver
from .. import backup_logger

log = backup_logger.get_logger(__name__)

class Zipper(BaseArchiver):

    archive_format = "zip"

    def archive(self, source_path: Path, destination_path: Path) -> Path:

        log.info(f"Starting archiving of directory '{source_path}' to {self.archive_format} format.")

        if not source_path.exists() or not source_path.is_dir():
            log.error(f"Source directory not found: {source_path}")
            raise FileNotFoundError(f"Source directory not found: {source_path}")

        try:
            archive_path_str = shutil.make_archive(
                base_name=str(destination_path),
                format=self.archive_format,
                root_dir=str(source_path)
            )
            archive_path = Path(archive_path_str)
            
            log.info(f"Archiving completed successfully. Archive saved to: {archive_path}")
            return archive_path
        
        except Exception as e:
            log.error(f"An error occurred during archiving: {e}", exc_info=True)
            raise
