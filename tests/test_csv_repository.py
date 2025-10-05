import os
import pytest
import pandas as pd
from core import csv_repository
from core.entities import Item, Stock

@pytest.fixture
def data_dir():
    """Fixture untuk path test_data."""
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "..", "test_data")

def test_load_items(data_dir):
    items_file = os.path.join(data_dir, "items.csv")
    items, scale = csv_repository.load_items(items_file)

    assert len(items) == 50
    assert scale == 1
    assert isinstance(items[0], Item)

def test_load_items2(data_dir):
    items_file = os.path.join(data_dir, "items2.csv")
    items, scale = csv_repository.load_items(items_file)

    assert len(items) == 8
    assert scale == 10
    assert isinstance(items[0], Item)

def test_load_stocks(data_dir):
    stocks_file = os.path.join(data_dir, "stocks.csv")
    stocks = csv_repository.load_stocks(stocks_file, scale=1)

    assert len(stocks) == 15
    assert all(isinstance(s, Stock) for s in stocks)
    s1 = stocks[0]
    assert s1.length == 5700
    assert s1.usable_length == 5650
    assert s1.unit_price == 100000

# class TestCSVRepository(unittest.TestCase):
#     def SetUp(self):
#         self.items_file = 'test_data/items.csv'
#         self.stocks_file = 'test_data/stocks.csv'

#     def test_load_items(self):
#         items, scale = csv_repository.load_items(self.items_file)
#         self.assertEqual(len(items), 7)
#         self.assertEqual(scale, 1)

#     def test_load_stocks(self):
#         stocks = csv_repository.load_stocks(self.stocks_file, scale=1)
#         self.assertEqual(len(stocks), 2)

    # def test_save_result(self):
    #     result = [
    #         {"pieces": [Item(type="A", length=50), Item(type="B", length=30)]},
    #         {"pieces": [Item(type="C", length=20)]}
    #     ]
    #     csv_repository.save_result(result, 'test_data/output.csv', scale=1)
    #     # Load the output file and verify its contents
    #     df = pd.read_csv('test_data/output.csv')
    #     self.assertEqual(len(df), 2)
    #     self.assertEqual(df.iloc[0]['used_length'], 8.0)  # (50+30)/10
    #     self.assertEqual(df.iloc[1]['used_length'], 2.0)  # 20/10