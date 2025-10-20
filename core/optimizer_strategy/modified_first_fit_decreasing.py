from core.optimizer_strategy import optimizer_strategy
from core.entities import Parts, Part, Stock

class modified_first_fit_decreasing(optimizer_strategy):
    def optimize(self, required_parts, available_stocks):
        results = []

    def sort_decreasing(self, required_parts):
        required_parts_sorted = sorted(required_parts, key=lambda x: x['length'], reverse=True)
        return required_parts_sorted

    def itemize_parts(self, required_parts):
        required_parts_itemize = []
        for row in required_parts:
            required_parts_itemize.extend(
                [Part(part_type=row["part_type"], length=row['length'])] * int(row["quantity"]))
        return required_parts_itemize
    
