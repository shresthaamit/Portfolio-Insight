from django.urls import path
from .views import PortfolioRiskAPIView,DiversificationAPIView

urlpatterns = [
    path(
        "portfolio-risk/<int:portfolio_id>/",
        PortfolioRiskAPIView.as_view(),
        name="portfolio-risk"
    ),
    path("diversification-score/<int:portfolio_id>/", DiversificationAPIView.as_view()
         ,name="diversification-score")
]