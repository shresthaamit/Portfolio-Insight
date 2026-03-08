from django.db import models
from django.conf import settings
class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.ticker


class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user})"


class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.FloatField()
    purchase_price = models.FloatField()
    purchase_date = models.DateField()

    class Meta:
        unique_together =('portfolio','stock')
    def __str__(self):
        return f"{self.stock.ticker} - {self.shares}"


class HistoricalPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField()
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField()
    volume = models.FloatField(null=True, blank=True)
    turnover = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('stock', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.stock.ticker} - {self.date}"
    

class Transaction(models.Model):
    BUY = "BUY"
    SELL = "SELL"

    TRANSACTION_TYPES = [
        (BUY, "Buy"),
        (SELL, "Sell"),
    ]

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    date = models.DateField()
    shares = models.PositiveIntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "id"]

    @property
    def total_amount(self):
        return self.shares * self.price

    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.ticker} - {self.transaction_type}"