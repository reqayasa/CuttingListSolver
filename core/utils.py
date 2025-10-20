import math

def detect_unit_scale(value: str) -> int:
    """
    Deteksi scale factor berdasarkan jumlah desimal
    """
    if '.' in value:
        decimals = len(value.split('.')[1])
        return 10 ** decimals
    return 1

def scale_value(value: float, scale: int) -> int:
    return int(round(value * scale))

def descale_value(value: int, scale: int) -> float:
    return value / scale
