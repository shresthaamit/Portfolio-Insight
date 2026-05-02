from rest_framework import serializers

class PortfolioRiskSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    portfolio_name = serializers.CharField()
    expected_return = serializers.FloatField()
    variance = serializers.FloatField()
    standard_deviation = serializers.FloatField()
    sharpe_ratio = serializers.FloatField()
    risk_level = serializers.CharField()


class DiversificationScoreSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    portfolio_name = serializers.CharField()
    diversification_score = serializers.FloatField()
    largest_stock = serializers.CharField()
    largest_stock_percentage = serializers.FloatField()
    sector_concentration = serializers.CharField()
    recommendation = serializers.CharField()

class PortfolioBenchmarkComparisonSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    portfolio_name = serializers.CharField()
    portfolio_return = serializers.FloatField()
    benchmark_return = serializers.FloatField()
    alpha = serializers.FloatField()
    status = serializers.CharField()