import shutil
import logging
from pathlib import Path
from .base import BaseArchiver

class Zipper(BaseArchiver):
    archive_format = "zip"

    def __init__(self, logger: logging.Logger):
        self.log = logger

    def archive(self, source_path: Path, destination_path: Path) -> Path:
        self.log.info(f"Starting archiving of directory '{source_path}' to {self.archive_format} format.")

        if not source_path.exists() or not source_path.is_dir():
            self.log.error(f"Source directory not found: {source_path}")
            raise FileNotFoundError(f"Source directory not found: {source_path}")

        try:
            archive_path_str = shutil.make_archive(
                base_name=str(destination_path),
                format=self.archive_format,
                root_dir=str(source_path)
            )
            archive_path = Path(archive_path_str)
            
            self.log.info(f"Archiving completed successfully. Archive saved to: {archive_path}")
            return archive_path
        
        except Exception as e:
            self.log.error(f"An error occurred during archiving: {e}", exc_info=True)
            raise