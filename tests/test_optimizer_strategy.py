import pytest
from core.optimizer_strategy import ColumnGeneration
from core.entities import Parts, Stock  # Adjust import path as needed

@pytest.fixture
def simple_parts_and_stocks():
    # 2 parts: length 3 (need 4), length 5 (need 2)
    # 1 stock: length 10 (have 3)
    parts = [
        Parts(part_type="A", length=3, quantity=4),
        Parts(part_type="B", length=5, quantity=2)
    ]
    stocks = [
        Stock(length=10, quantity=3)
    ]
    return parts, stocks

def test_generate_trivial_patterns(simple_parts_and_stocks):
    parts, stocks = simple_parts_and_stocks
    cg = ColumnGeneration()
    patterns = cg.generate_trivial_patterns(parts, stocks)
    assert any(p['pattern'] == (3, 0) and p['waste'] == 1 for p in patterns)
    assert any(p['pattern'] == (0, 2) and p['waste'] == 0 for p in patterns)
    assert len(patterns) == 2

def test_solve_unbounded_knapsack_basic():
    cg = ColumnGeneration()
    values = [10, 20]
    weights = [2, 3]
    capacity = 7
    best_value, counts = cg.solve_unbounded_knapsack(values, weights, capacity)
    # The DP implementation finds the best achievable value for some capacity <= 7.
    # Instead of asserting an exact counts vector (there may be multiple optimal packings),
    # verify the returned value and that the counts form a feasible packing that achieves it.
    assert best_value == 40
    assert isinstance(counts, list)
    assert all(isinstance(c, int) and c >= 0 for c in counts)
    # total value matches best_value
    total_value = sum(v * c for v, c in zip(values, counts))
    assert total_value == best_value
    # total weight does not exceed capacity
    total_weight = sum(w * c for w, c in zip(weights, counts))
    assert total_weight <= capacity
 
def test_optimize_simple_case(simple_parts_and_stocks):
    parts, stocks = simple_parts_and_stocks
    # Ensure a fresh optimizer instance for each test run to avoid overlapping constraint names in PuLP
    cg = ColumnGeneration()
    patterns = cg.optimize(parts, stocks)
    assert any(p['pattern'] == (3, 0) for p in patterns)
    assert any(p['pattern'] == (0, 2) for p in patterns)
    for p in patterns:
        assert 'stock_index' in p
        assert 'stock_length' in p
        assert 'pattern' in p
        assert 'waste' in p

def test_generate_trivial_patterns_no_possible_pattern():
    cg = ColumnGeneration()
    parts = [Parts(part_type="A", length=15, quantity=1)]
    stocks = [Stock(length=10, quantity=1)]
    patterns = cg.generate_trivial_patterns(parts, stocks)
    assert patterns == []

def test_optimize_raises_on_no_trivial_patterns():
    cg = ColumnGeneration()
    parts = [Parts(part_type="A", length=15, quantity=1)]
    stocks = [Stock(length=10, quantity=1)]
    with pytest.raises(ValueError):
        cg.optimize(parts, stocks)
