from core.optimizer_strategy import ColumnGeneration

class OptimizerService:
    def __init__(self, strategy=None):
        self.strategy = strategy or ColumnGeneration()
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def run(self, required_parts, required_stocks):
        return self.strategy.optimize(required_parts, required_stocks)