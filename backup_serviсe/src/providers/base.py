from abc import ABC, abstractmethod
from pathlib import Path

class BaseProvider(ABC):

    @abstractmethod
    def upload(self, file_path: Path) -> None:
        pass