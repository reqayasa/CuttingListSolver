from core.optimizer_strategy import GreedyOptimizer

class OptimizerService:
    def __init__(self, strategy=None):
        self.strategy = strategy or GreedyOptimizer()
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def run(self, items, stocks, allow_overcut=0.02):
        return self.strategy.optimize(items, stocks, allow_overcut)