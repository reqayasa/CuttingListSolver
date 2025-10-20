import pandas as pd
import pulp
from core.entities import Part, Parts, Stock
from core.utils import detect_unit_scale, scale_value, descale_value
from collections import defaultdict

def load_required_parts(filename: str):
    df = pd.read_csv(filename)
    normalized_parts = []
    unit_scale = 1

    # Deteksi skala terbesar dari semua input
    for _, row in df.iterrows():
        unit_scale = max(unit_scale, detect_unit_scale(str(row["length"])))
    
    # Load required parts dengan skala yang sudah ditentukan (normalisasi)
    for _, row in df.iterrows():
        length_normalized = scale_value(float(row["length"]), unit_scale)
        normalized_parts.extend([Part(part_type=row["part_type"], length=length_normalized)] * int(row["quantity"]))

    return normalized_parts, unit_scale

def load_required_parts_aggreageted(filename: str):
    df = pd.read_csv(filename)
    normalized_parts_aggregated = []
    unit_scale = 1

    # Deteksi skala terbesar dari semua input
    for _, row in df.iterrows():
        unit_scale = max(unit_scale, detect_unit_scale(str(row["length"])))
    
    # Load required parts dengan skala yang sudah ditentukan (normalisasi)
    for _, row in df.iterrows():
        length_normalized = scale_value(float(row["length"]), unit_scale)
        normalized_parts_aggregated.extend([Parts(
            part_type = row["part_type"], 
            length = length_normalized,
            quantity = int(row["quantity"])
            )])

    return normalized_parts_aggregated, unit_scale

def load_stocks(filename: str, unit_scale: int):
    df = pd.read_csv(filename)  
    normalized_stocks = []

    for _, row in df.iterrows():
        normalized_stocks.extend([Stock(
            length = scale_value(float(row["length"]), unit_scale),
            quantity = 1,
        )] * int(row["quantity"]))
    return normalized_stocks

def load_stocks_aggregated(filename: str, unit_scale: int):
    df = pd.read_csv(filename)  
    normalized_stocks_aggregated = []

    for _, row in df.iterrows():
        normalized_stocks_aggregated.extend([Stock(
            length = scale_value(float(row["length"]), unit_scale),
            quantity = int(row["quantity"]),
        )])
    return normalized_stocks_aggregated

def save_result(result, filename: str, unit_scale: int):
    rows = []
    for i, bar in enumerate(result):
        used = sum(p.length for p in bar)
        rows.append({
            "stock_id": i + 1,
            "used_length": round(descale_value(used, unit_scale), 2),
            "pieces": " | ".join(str(round(descale_value(p.length, unit_scale), 2)) for p in bar)
        })
    pd.DataFrame(rows).to_csv(filename, index=False)
