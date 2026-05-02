import math
from collections import defaultdict
from Portfolio.models import Portfolio, Transaction, HistoricalPrice

def get_portfolio_risk_analysis(portfolio_id, user =None):
    portfolio = Portfolio.objects.filter(id = portfolio_id).first()
    if not portfolio:
        raise ValueError("Portfolio not found")
    if user and portfolio.user !=user:
        raise PermissionError("You do not have permission to access this portfolio.")
    
    transactions = (
        Transaction.objects
        .select_related("stock")
        .filter(portfolio=portfolio)
        .order_by("date","id")
    )
    if not transactions.exists():
        return{
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "expected_return": 0,
            "variance": 0,
            "standard_deviation": 0,
            "sharpe_ratio": 0,
            "risk_level": "No Data"
        }

    shares_by_stock = defaultdict(float)
    for txn in transactions:
        if txn.transaction_type == "BUY":
            shares_by_stock[txn.stock_id] += txn.shares

        elif txn.transaction_type =="SELL":
            shares_by_stock[txn.stock_id] -= txn.shares

    stock_returns = []

    for stock_id, shares in shares_by_stock.items():
        if shares <= 0:
            continue
        prices = (
            HistoricalPrice.objects.filter(stock_id=stock_id)
            .order_by("date")

        )
        if prices.count() <2:
            continue

        first_price = prices.first().close_price
        latest_price = prices.last().close_price

        if first_price == 0:
            continue

        stock_return = ((latest_price - first_price)/ first_price) * 100
        stock_returns.append(stock_return)

    if not stock_returns:
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "expected_return": 0,
            "variance": 0,
            "standard_deviation": 0,
            "sharpe_ratio": 0,
            "risk_level": "No Data"
        }
    
    expected_return = sum(stock_returns) / len(stock_returns)

    variance = sum(
        (r - expected_return) ** 2 for r in stock_returns)/ len(stock_returns)
    standard_deviation = math.sqrt(variance)
    risk_free_rate = 5
    if standard_deviation  == 0:
        sharpe_ratio = 0

    else:
        sharpe_ratio = (expected_return - risk_free_rate) / standard_deviation

    if standard_deviation < 10:
        risk_level = 'Low'
    elif standard_deviation <20:
        risk_level = 'Modernate'

    else:
        risk_level = 'High'


    return{
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "expected_return": round(expected_return, 2),
        "variance": round(variance, 2),
        "standard_deviation": round(standard_deviation, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "risk_level": risk_level
    }



