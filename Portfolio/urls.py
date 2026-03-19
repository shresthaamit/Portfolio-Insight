from django.urls import path
from .views import *

urlpatterns = [
    # path('loadmarket/', LoadMarketDataView.as_view()),
    path('loaddata/', LoadMarketDataView, name='load_data'),
    path('loadsample/', sample_view, name='loadsample'),
    path("market/history/",MarketHistoryView.as_view(), name="marketHistory"),
    path("market/latest/", MarketLatestView.as_view(), name="market-latest"),
    path("market/series/",MarketSeriesView.as_view(),name="marketSeries"),
    path("market/symbols/",MarketSymbolView.as_view(),name="marketSymbols"),
    path("market/stocks/", MarketStocksView.as_view(), name="market-stocks"),
    path("portfolios/", PortfolioListCreateView.as_view(), name="portfolio-list-create"),

    path("stock-price/", StockPriceView.as_view(), name="stock-price"),
    path("transactions/buy/", BuyTransactionView.as_view(), name="buy-transaction"),
    path(
    "transactions/sell/",SellTransactionView.as_view(),
    name="sell-transaction"
),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("holdings/", HoldingListView.as_view(), name="holding-list"),
    path("portfolio-summary/", PortfolioSummaryView.as_view(), name="portfolio-summary"),
    path(
        "analytics/sector-allocation/<int:portfolio_id>/",
        SectorAllocationAPIView.as_view(),
        name="sector-allocation",
    ),
        path("analytics/portfolio-trend/<int:portfolio_id>/", PortfolioTrendAPIView.as_view(), name="portfolio-trend"),
        path(
        "analytics/portfolio-value/<int:portfolio_id>/",
        PortfolioValueAPIView.as_view(),
        name="portfolio-value"),
        path(
            "analytics/portfolio-holdings/<int:portfolio_id>/",
            PortfolioHoldingAPIView.as_view(),
            name="portfolio-holdings",
),
        





]
