from dataclasses import dataclass

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