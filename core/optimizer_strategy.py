from abc import ABC, abstractmethod

class OptimizerStrategy(ABC):
    @abstractmethod
    def optimize(self, items, stock, allow_overcut=0.02):
        pass

class GreedyOptimizer(OptimizerStrategy):
    def optimize(self, items, stock, allow_overcut=0.02):
        items = sorted(items, key=lambda x: x.length, reverse=True)
        bins = []

        # expand stock sesuai quantity
        expanded_stock = []
        for s in stock:
            for _ in range(s.quantity):
                expanded_stock.append({
                    "stock_length": s.length,
                    "usable_length": s.usable_length,
                    "max_allowed": int(s.usable_length * (1 + allow_overcut)),
                    "pieces": []
                })

        for item in items:
            placed = False
            for b in expanded_stock:
                used = sum(p.length for p in b["pieces"])
                if used + item.length <= b["max_allowed"] and used + item.length <= b["stock_length"]:
                    b["pieces"].append(item)
                    placed = True
                    break
            if not placed:
                # jika tidak ada stok tersedia -> masuk ke "unplaced"
                bins.append([item])
        return expanded_stock