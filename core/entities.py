from dataclasses import dataclass
import pandas as pd

@dataclass
class Part:
    part_type: str
    length: int # dalam satuan scaled integer (normalize)

@dataclass
class Parts:
    part_type: str
    length: int # dalam satuan scaled integer (normalize)
    quantity: int

@dataclass
class Stock:
    length: int # dalam satuan scaled integer (normalize)
    quantity: int

@dataclass
class CutPiece:
    part_id: str
    length: int
    stock_id: str
    position: int | None = None


@dataclass
class CutPattern:
    stock_id: str
    stock_length: int
    used_length: int
    waste: int
    pieces: list[CutPiece]
    pattern_index: int


@dataclass
class CuttingStockOutput:
    patterns: list[CutPattern]

    def to_dataframe(self):
        """Normalized table for CSV export or computation."""
        rows = []
        for p in self.patterns:
            for piece in p.pieces:
                rows.append({
                    "pattern_index": p.pattern_index,
                    "stock_id": p.stock_id,
                    "stock_length": p.stock_length,
                    "part_id": piece.part_id,
                    "part_length": piece.length,
                    "position": piece.position,
                    "waste": p.waste,  # repeated on all rows
                })
        return pd.DataFrame(rows)