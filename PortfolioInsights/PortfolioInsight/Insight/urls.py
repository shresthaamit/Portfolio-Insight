from django.urls import path
from .views import PortfolioRiskAPIView,DiversificationAPIView,BenchmarkGenerateAPIView,PortfolioBenchmarkComparisionAPIView

urlpatterns = [
    path(
        "portfolio-risk/<int:portfolio_id>/",
        PortfolioRiskAPIView.as_view(),
        name="portfolio-risk"
    ),
    path("diversification-score/<int:portfolio_id>/", DiversificationAPIView.as_view()
         ,name="diversification-score"),
    path("benchmark/generate/", BenchmarkGenerateAPIView.as_view()),
    path(
    "portfolio-vs-benchmark/<int:portfolio_id>/",
   
    PortfolioBenchmarkComparisionAPIView.as_view(),
    name="portfolio-vs-benchmark"
),
]