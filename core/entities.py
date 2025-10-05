from dataclasses import dataclass

@dataclass
class Item:
    type: str
    length: int # dalam satuan scaled integer

@dataclass
class Stock:
    length: int
    usable_length: int
    quantity: int
    unit_price: float = 0.0