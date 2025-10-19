import os
import pytest
import pandas as pd
from core.csv_repository import load_required_parts, load_stocks
from core.entities import Part, Stock

@pytest.fixture
def data_dir():
    """Fixture untuk path test_data."""
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "..", "test_data")

def test_load_required_parts_basic(data_dir):
    """Test loading parts with decimal measurements.
    Tests that floating point values are properly normalized to integers:
    - 1.000 -> 10 (scale=10)
    - 2.500 -> 25 (using same scale)
    """
    parts, unit_scale = load_required_parts(os.path.join(data_dir, "test_basic.csv"))

    assert unit_scale == 10  # Scale based on decimal precision needed
    assert len(parts) == 3   # 2 of type A + 1 of type B
    assert all(isinstance(p, Part) for p in parts)
    
    # Check the two type A parts (1.000 normalized to 10)
    assert parts[0].part_type == "A"
    assert parts[0].length == 10  # 1.000 * 10
    assert parts[1].part_type == "A"
    assert parts[1].length == 10  # 1.000 * 10
    
    # Check the type B part (2.500 normalized to 25)
    assert parts[2].part_type == "B"
    assert parts[2].length == 25  # 2.500 * 10

def test_load_required_parts_empty(data_dir):
    """Test loading an empty parts list.
    Should return empty list and default scale of 1.
    """
    parts, unit_scale = load_required_parts(os.path.join(data_dir, "test_empty.csv"))
    assert parts == []
    assert unit_scale == 1  # No decimals, so no scaling needed

def test_load_required_parts_quantity_multiple(data_dir):
    """Test loading multiple quantities of the same part.
    Tests that:
    1. Quantity is respected (3 copies created)
    2. Integer values don't affect scaling (500 stays 500)
    """
    parts, unit_scale = load_required_parts(os.path.join(data_dir, "test_quantity_multiple.csv"))
    assert unit_scale == 1  # No decimals in input, so no scaling needed
    assert len(parts) == 3  # Quantity of 3 in CSV
    assert all(p.part_type == "X" for p in parts)
    assert all(p.length == 500 for p in parts)  # Integer input remains unchanged

def test_load_stocks_basic(data_dir):
    """Test loading stocks with decimal measurements.
    Tests that floating point values are properly normalized based on provided scale:
    - 3.000 -> 30 (with unit_scale=10)
    """
    stocks = load_stocks(os.path.join(data_dir, "test_stocks_basic.csv"), unit_scale=10)
    
    assert len(stocks) == 2  # Total quantity from CSV
    assert all(isinstance(s, Stock) for s in stocks)
    assert all(s.length == 30 for s in stocks)  # 3.000 * 10
    assert all(s.quantity == 1 for s in stocks)

def test_load_stocks_empty(data_dir):
    """Test loading an empty stocks list."""
    stocks = load_stocks(os.path.join(data_dir, "test_stocks_empty.csv"), unit_scale=1)
    assert stocks == []

def test_load_stocks_quantity_multiple(data_dir):
    """Test loading multiple quantities of the same stock.
    Tests that quantity is respected (3 copies created).
    """
    stocks = load_stocks(os.path.join(data_dir, "test_stocks_quantity.csv"), unit_scale=1)
    
    assert len(stocks) == 3  # Quantity of 3 from CSV
    assert all(s.length == 1000 for s in stocks)
    assert all(s.quantity == 1 for s in stocks)

