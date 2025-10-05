import pandas as pd
from core.entities import Item, Stock
from core.utils import detect_scale, scale_value, descale_value

def load_items(filename: str):
    df = pd.read_csv(filename)
    items = []
    scale = 1

    # Deteksai skala terbesar dari semua input
    for _, row in df.iterrows():
        scale = max(scale, detect_scale(str(row["length"])))
    
    # Load items dengan skala yang sudah ditentukan
    for _, row in df.iterrows():
        length_scaled = scale_value(float(row["length"]), scale)
        items.extend([Item(type=row["type"], length=length_scaled)] * int(row["quantity"]))

    return items, scale

def load_stocks(filename: str, scale: int):
    df = pd.read_csv(filename)
    stock = []

    for _, row in df.iterrows():
        stock.extend([Stock(
            length=scale_value(float(row["length"]), scale),
            usable_length=scale_value(float(row["usable_length"]), scale),
            quantity=1,
            unit_price=float(row.get("unit_price", 0))
        )] * int(row["quantity"]))
    return stock

def save_result(result, filename: str, scale: int):
    rows = []
    for i, bar in enumerate(result):
        used = sum(p.length for p in bar)
        rows.append({
            "stock_id": i + 1,
            "used_length": round(descale_value(used, scale), 2),
            "pieces": " | ".join(str(round(descale_value(p.length, scale), 2)) for p in bar)
        })
    pd.DataFrame(rows).to_csv(filename, index=False)