from pprint import pprint
from core.optimizer_strategy.optimizer_strategy import OptimizerStrategy
from core.entities import Parts, Part, Stock

class ModifiedFirstFitDecreasing(OptimizerStrategy):
    def optimize(self, required_parts, available_stocks):
        required_parts = self.sort_decreasing(required_parts)
        required_parts = self.itemize_parts(required_parts)
        pprint(required_parts)

    def sort_decreasing(self, required_parts):
        required_parts_sorted = sorted(required_parts, key=lambda x: x.length, reverse=True)
        return required_parts_sorted

    def itemize_parts(self, required_parts):
        required_parts_itemize = []
        for row in required_parts:
            required_parts_itemize.extend(
                [Part(part_type=row.part_type, length=row.length)] * int(row.quantity))
        return required_parts_itemize
    
    # def calssify_parts(self, parts):
    #     type1 = [part for part in parts if part[1] > 1200]

    
