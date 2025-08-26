from abc import ABC, abstractmethod
from pathlib import Path

class BaseArchiver(ABC):

    @abstractmethod
    def archive(self, source_path: Path, destination_path: Path) -> Path:
        pass