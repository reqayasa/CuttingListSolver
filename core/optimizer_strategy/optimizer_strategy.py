from abc import ABC, abstractmethod

class OptimizerStrategy(ABC):
    @abstractmethod
    def optimize(self, required_parts, available_stocks):
        pass