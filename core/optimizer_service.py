from pprint import pprint
from core.optimizer_strategy.column_generation import ColumnGeneration
from core.optimizer_strategy.modified_first_fit_decreasing import ModifiedFirstFitDecreasing 
# from core.compatible_export import aggregate_and_export_from_trivial
from core.compatible_export import export_pattern_summary

class OptimizerService:
    def __init__(self, strategy=None):
        self.strategy = strategy or ColumnGeneration()
    
    def set_strategy(self, strategy):
        self.strategy = strategy
     
    def run(self, required_parts, stocks):
        # Jalankan optimasi
        results = self.strategy.optimize(required_parts, stocks)
        patterns = []

        # # Sesuaikan jumlah nilai yang direturn
        # # Bisa (patterns, x_values, x_int) atau (patterns, x_int)
        # if len(results) == 3:
        #     patterns, x_values, x_int = results
        # else:
        #     patterns, x_int = results
        #     x_values = None  # fallback

        # # Tentukan hasil yang digunakan
        # x_used = x_int if x_int else x_values

        # # Ekspor summary pattern
        # res2 = export_pattern_summary(
        #     self,          # <- kalau fungsi export tidak butuh class ini, hapus 'self'
        #     patterns,
        #     x_used,
        #     required_parts
        # )

        # # Debug print
        # print("\n=== Patterns ===")
        # pprint(patterns)
        # print("\n=== X used ===")
        # pprint(x_used)
        # print("\n=== X values (LP) ===")
        # pprint(x_values)

        # # return patterns, x_used
        return patterns
    
