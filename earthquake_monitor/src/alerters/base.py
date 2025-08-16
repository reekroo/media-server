from abc import ABC, abstractmethod

class Alerter(ABC):
    
    @abstractmethod
    def trigger_alert(self, melody_name, duration):
        pass