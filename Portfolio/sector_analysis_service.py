from collections import defaultdict

from .models import Holding, Portfolio


def get_sector_allocation(portfolio_id, user=None):
    """
    Returns sector-wise invested allocation for a portfolio.

    V1 logic:
    invested_value = shares * purchase_price
    allocation_percent = sector_invested / total_invested * 100
    """

    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if not portfolio:
        raise ValueError("Portfolio not found.")

    if user and portfolio.user != user:
        raise PermissionError("You do not have permission to access this portfolio.")

    holdings = (
        Holding.objects
        .select_related("stock")
        .filter(portfolio=portfolio, shares__gt=0)
    )

    sector_map = defaultdict(lambda: {
        "sector": "",
        "invested_value": 0.0,
        "holding_count": 0,
    })

    total_invested = 0.0

    for holding in holdings:
        sector_name = holding.stock.sector or "Unknown"
        invested_value = float(holding.shares) * float(holding.purchase_price)

        sector_map[sector_name]["sector"] = sector_name
        sector_map[sector_name]["invested_value"] += invested_value
        sector_map[sector_name]["holding_count"] += 1

        total_invested += invested_value

    sectors = []
    for _, item in sector_map.items():
        allocation_percent = (
            (item["invested_value"] / total_invested) * 100
            if total_invested > 0 else 0
        )

        sectors.append({
            "sector": item["sector"],
            "invested_value": round(item["invested_value"], 2),
            "allocation_percent": round(allocation_percent, 2),
            "holding_count": item["holding_count"],
        })

    sectors.sort(key=lambda x: x["invested_value"], reverse=True)

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "total_invested": round(total_invested, 2),
        "sectors": sectors,
    }