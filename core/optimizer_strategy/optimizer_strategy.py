from abc import ABC, abstractmethod

class optimizer_strategy(ABC):
    @abstractmethod
    def optimize(self, required_parts, available_stocks):
        pass