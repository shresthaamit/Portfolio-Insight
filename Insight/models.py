
from django.db import models

class MarketBenchmark(models.Model):
    date = models.DateField(unique=True)
    value = models.FloatField()

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} - {self.value}"