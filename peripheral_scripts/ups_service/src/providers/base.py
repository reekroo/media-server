from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class UpsReading:
    soc_percent: float   # 0..100
    voltage_v: float     # for example 3.7..4.2
    ac_present: bool     # adapter is present

class UpsProvider(ABC):
    
    @abstractmethod
    def read(self) -> UpsReading: ...

    @abstractmethod
    def cleanup(self) -> None: ...