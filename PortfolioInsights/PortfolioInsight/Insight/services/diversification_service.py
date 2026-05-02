from Portfolio.models import Portfolio, Holding,HistoricalPrice

from Insight.models import MarketBenchmark
def get_diversification_score(portfolio_id, user=None):
    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if not portfolio:
        raise ValueError("Portfolio not found.")

    if user and portfolio.user != user:
        raise PermissionError("You do not have permission to access this portfolio.")

    holdings = Holding.objects.filter(portfolio=portfolio).select_related("stock")

    if not holdings.exists():
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "diversification_score": 0,
            "largest_stock": "None",
            "largest_stock_percentage": 0,
            "sector_concentration": "No Data",
            "recommendation": "No holdings available"
        }

    total_investment = sum(
        h.shares * h.purchase_price for h in holdings
    )

    if total_investment == 0:
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "diversification_score": 0,
            "largest_stock": "None",
            "largest_stock_percentage": 0,
            "sector_concentration": "No Data",
            "recommendation": "Investment value is zero"
        }

    largest_stock = ""
    largest_stock_percentage = 0

    for h in holdings:
        stock_value = h.shares * h.purchase_price
        percentage = (stock_value / total_investment) * 100

        if percentage > largest_stock_percentage:
            largest_stock_percentage = percentage
            largest_stock = h.stock.ticker

    diversification_score = 100 - largest_stock_percentage

    if largest_stock_percentage >= 60:
        sector_concentration = "High"
        recommendation = "Reduce concentration in one stock"
    elif largest_stock_percentage >= 40:
        sector_concentration = "Moderate"
        recommendation = "Portfolio is moderately concentrated"
    else:
        sector_concentration = "Low"
        recommendation = "Portfolio is well diversified"

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "diversification_score": round(diversification_score, 2),
        "largest_stock": largest_stock,
        "largest_stock_percentage": round(largest_stock_percentage, 2),
        "sector_concentration": sector_concentration,
        "recommendation": recommendation
    }




def get_portfolio_vs_benchmark(portfolio_id, user = None):
    portfolio = Portfolio.objects.filter(id= portfolio_id).first()
    if not portfolio:
        raise ValueError("Portfolio not found.")
    if user and portfolio.user != user:
        raise PermissionError("You donot have permission.")
    holdings  = Holding.objects.filter(portfolio=portfolio)
    if not holdings.exists():
        raise ValueError("No holding found in portfolio")
    total_investment = 0
    current_value = 0
    for holding in holdings:
        investment  = holding.shares * holding.purchase_price
        latest_price_obj = (
            HistoricalPrice.objects
            .filter(stock = holding.stock)
            .order_by("-date")
            .first()

        )
        latest_price  =  latest_price_obj.close_price if latest_price_obj else 0
        value = holding.shares * latest_price
        total_investment += investment
        current_value += value


    if total_investment == 0:
        raise ValueError("Total investment is zero")
    
    portfolio_return = (
        (current_value - total_investment)/total_investment
    ) * 100
    first_benchmark = MarketBenchmark.objects.order_by("date").first()
    latest_benchmark = MarketBenchmark.objects.order_by("-date").first()

    if not first_benchmark or not latest_benchmark:
        raise ValueError("Benchmark data not found")
    benchmark_return = (
        (latest_benchmark.value - first_benchmark.value)
        / first_benchmark.value
    ) * 100
    alpha = portfolio_return - benchmark_return

    if alpha >0:
        status = "Outperforming"
    elif alpha < 0:
        status = "Underperforming"

    else:
        status = "Matching Benchmark"

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "portfolio_return": round(portfolio_return, 2),
        "benchmark_return": round(benchmark_return, 2),
        "alpha": round(alpha, 2),
        "status": status
    }