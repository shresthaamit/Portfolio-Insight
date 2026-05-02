from django.test import TestCase
from .models import Stock

class StockModelTest(TestCase):

    def setUp(self):
        Stock.objects.create(name="Apple", price=150)

    def test_stock_creation(self):
        stock = Stock.objects.get(name="Apple")
        self.assertEqual(stock.price, 150)