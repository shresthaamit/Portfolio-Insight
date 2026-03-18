from .models import *
from rest_framework import serializers

class MarketHistorySerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source = "stock.ticker")
    class Meta:
        model = HistoricalPrice
        fields = ["symbol", "date", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"]

class MarketLatestSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="stock.ticker")

    class Meta:
        model = HistoricalPrice
        fields = ["symbol", "date", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"]

class MarketSeriesPointSerializer(serializers.ModelSerializer):
    close = serializers.FloatField(source="close_price")
    class Meta:
        model = HistoricalPrice
        fields = ["date","close"]

class StockMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["ticker", "name", "sector"]

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class TransactionSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source="stock.ticker", read_only=True)
    stock_name = serializers.CharField(source="stock.name", read_only=True)
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "portfolio",
            "portfolio_name",
            "stock",
            "ticker",
            "stock_name",
            "transaction_type",
            "date",
            "shares",
            "price",
            "total_amount",
            "created_at",
        ]


class BuyTransactionSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    ticker = serializers.CharField()
    date = serializers.DateField()
    shares = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        try:
            portfolio = Portfolio.objects.get(id=attrs["portfolio_id"], user=user)
        except Portfolio.DoesNotExist:
            raise serializers.ValidationError({"portfolio_id": "Portfolio not found."})

        ticker = attrs["ticker"].strip().upper()

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            raise serializers.ValidationError({"ticker": "Stock not found."})

        try:
            historical_price = HistoricalPrice.objects.get(
                stock=stock,
                date=attrs["date"]
            )
        except HistoricalPrice.DoesNotExist:
            raise serializers.ValidationError({
                "date": "No historical price found for this stock on selected date."
            })

        attrs["portfolio"] = portfolio
        attrs["stock"] = stock
        attrs["historical_price"] = historical_price
        attrs["ticker"] = ticker
        return attrs


class SellTransactionSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    ticker = serializers.CharField()
    date = serializers.DateField()
    shares = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        try:
            portfolio = Portfolio.objects.get(id=attrs["portfolio_id"], user=user)
        except Portfolio.DoesNotExist:
            raise serializers.ValidationError("Portfolio not found")

        ticker = attrs["ticker"].strip().upper()

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            raise serializers.ValidationError("Stock not found")

        try:
            holding = Holding.objects.get(portfolio=portfolio, stock=stock)
        except Holding.DoesNotExist:
            raise serializers.ValidationError("No holdings for this stock")

        if attrs["shares"] > holding.shares:
            raise serializers.ValidationError("Not enough shares to sell")

        try:
            price = HistoricalPrice.objects.get(
                stock=stock,
                date=attrs["date"]
            )
        except HistoricalPrice.DoesNotExist:
            raise serializers.ValidationError("No historical price for this date")

        attrs["portfolio"] = portfolio
        attrs["stock"] = stock
        attrs["holding"] = holding
        attrs["price"] = price.close_price

        return attrs
    

class HoldingSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source="stock.ticker", read_only=True)
    stock_name = serializers.CharField(source="stock.name", read_only=True)
    average_price = serializers.SerializerMethodField()
    total_investment = serializers.SerializerMethodField()

    class Meta:
        model = Holding
        fields = [
            "id",
            "ticker",
            "stock_name",
            "shares",
            "average_price",
            "purchase_date",
            "total_investment",
        ]

    def get_average_price(self, obj):
        return round(obj.purchase_price, 2)

    def get_total_investment(self, obj):
        return round(obj.shares * obj.purchase_price, 2)
    

class SectorAllocationItemSerializer(serializers.Serializer):
    sector = serializers.CharField()
    invested_value =serializers.FloatField()
    allocation_percent = serializers.FloatField()
    holding_count = serializers.IntegerField()

class SectorAllocationSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    portfolio_name = serializers.CharField()
    total_invested = serializers.FloatField()
    sectors = SectorAllocationItemSerializer(many=True)

class PortfolioTrendPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    value = serializers.FloatField()


class PortfolioTrendSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    portfolio_name = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    start_value = serializers.FloatField()
    end_value = serializers.FloatField()
    return_percent = serializers.FloatField()
    trend = PortfolioTrendPointSerializer(many=True)