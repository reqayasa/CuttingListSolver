# import os
import pytest
from core.entities import Part, Parts, Stock
from core.optimizer_strategy.modified_first_fit_decreasing import ModifiedFirstFitDecreasing
from pprint import pprint

# @pytest.fixture
# def data_dir():
#     """Fixture untuk path test_data."""
#     base_dir = os.path.dirname(__file__)
#     return os.path.join(base_dir, "..", "test_data")

@pytest.fixture
def raw_data():
    parts = [
        Parts(part_type="A", length=1200, quantity=4),
        Parts(part_type="B", length=800, quantity=6),
        Parts(part_type="C", length=450, quantity=10),
        Parts(part_type="D", length=1500, quantity=2),
        Parts(part_type="E", length=600, quantity=8),
    ]
    stocks = [
        Stock(length=2400, quantity=100)
    ]
    return parts, stocks

@pytest.fixture
def sorted_data():
        parts = [
            Parts(part_type="A", length=1200, quantity=4),
            Parts(part_type="B", length=800, quantity=2),
        ]
        stocks = [Stock(length=2400, quantity=100)]
        return parts, stocks
        
def test_sort_decreasing(raw_data):
    parts, stocks = raw_data
    opt = ModifiedFirstFitDecreasing()
    sorted_list = opt.sort_decreasing(parts)

    lengths = [p.length for p in sorted_list]
    assert lengths == [1500, 1200, 800, 600, 450]

def test_itemize_parts(sorted_data):
    parts, stocks = sorted_data
    opt = ModifiedFirstFitDecreasing()

    itemized = opt.itemize_parts(parts)
    pprint(itemized)

    # Total parts yang dihasilkan = jumlah quantity
    assert len(itemized) == sum(p.quantity for p in parts)

    # Semua hasil itemize harus berupa instance dari Part
    assert all(isinstance(p, Part) for p in itemized)

    # Cek bahwa jumlah setiap part_type benar
    from collections import Counter
    counts = Counter(p.part_type for p in itemized)

    assert counts["A"] == 4
    assert counts["B"] == 2

    # Cek urutan awal tetap sesuai
    assert itemized[0].part_type == "A"
    assert itemized[-1].part_type == "B"

    
