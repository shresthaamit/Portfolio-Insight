from collections import defaultdict
from datetime import datetime

from Portfolio.models import Portfolio, Transaction, HistoricalPrice,Stock


def get_portfolio_trend(portfolio_id, user=None, start_date=None, end_date=None):
    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if not portfolio:
        raise ValueError("Portfolio not found.")

    if user and portfolio.user != user:
        raise PermissionError("You do not have permission to access this portfolio.")

    transactions = (
        Transaction.objects
        .select_related("stock")
        .filter(portfolio=portfolio)
        .order_by("date", "id")
    )

    if not transactions.exists():
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "trend": []
        }

    first_txn_date = transactions.first().date

    # parse optional dates
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if start_date < first_txn_date:
            start_date = first_txn_date
    else:
        start_date = first_txn_date

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    stock_ids = transactions.values_list("stock_id", flat=True).distinct()

    all_prices = HistoricalPrice.objects.filter(stock_id__in=stock_ids)

    if end_date:
        all_prices = all_prices.filter(date__lte=end_date)

    all_prices = all_prices.order_by("date")

    if not all_prices.exists():
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "trend": []
        }

    trend_dates = sorted(set(
        p.date for p in all_prices if p.date >= start_date
    ))

    trend = []

    for current_date in trend_dates:
        shares_by_stock = defaultdict(int)

        txns_up_to_date = transactions.filter(date__lte=current_date)

        for txn in txns_up_to_date:
            if txn.transaction_type == Transaction.BUY:
                shares_by_stock[txn.stock_id] += txn.shares
            elif txn.transaction_type == Transaction.SELL:
                shares_by_stock[txn.stock_id] -= txn.shares

        total_value = 0.0

        for stock_id, net_shares in shares_by_stock.items():
            if net_shares <= 0:
                continue

            price_obj = (
                HistoricalPrice.objects
                .filter(stock_id=stock_id, date=current_date)
                .first()
            )

            if price_obj:
                total_value += net_shares * price_obj.close_price

        trend.append({
            "date": current_date,
            "value": round(total_value, 2)
        })
        # ===== ADD THIS BLOCK =====

    start_value = trend[0]["value"] if trend else 0
    end_value = trend[-1]["value"] if trend else 0

    start_date_val = trend[0]["date"] if trend else None
    end_date_val = trend[-1]["date"] if trend else None

    return_percent = 0
    if start_value > 0:
        return_percent = ((end_value - start_value) / start_value) * 100

        # ===== END BLOCK =====

    return {
         "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "start_date": start_date_val,
        "end_date": end_date_val,
        "start_value": start_value,
        "end_value": end_value,
        "return_percent": round(return_percent, 2),
        "trend": trend
    }  




def get_portfolio_value_on_date(portfolio_id, date, user=None):
    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if not portfolio:
        raise ValueError("Portfolio not found.")

    if user and portfolio.user != user:
        raise PermissionError("You do not have permission to access this portfolio.")

    if not date:
        raise ValueError("date query parameter is required.")

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    transactions = (
        Transaction.objects
        .select_related("stock")
        .filter(portfolio=portfolio, date__lte=target_date)
        .order_by("date", "id")
    )

    if not transactions.exists():
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "date": target_date,
            "value": 0.0
        }

    shares_by_stock = defaultdict(int)

    for txn in transactions:
        if txn.transaction_type == Transaction.BUY:
            shares_by_stock[txn.stock_id] += txn.shares
        elif txn.transaction_type == Transaction.SELL:
            shares_by_stock[txn.stock_id] -= txn.shares

    total_value = 0.0

    for stock_id, net_shares in shares_by_stock.items():
        if net_shares <= 0:
            continue

        price_obj = (
            HistoricalPrice.objects
            .filter(stock_id=stock_id, date=target_date)
            .first()
        )

        if price_obj:
            total_value += net_shares * price_obj.close_price

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "date": target_date,
        "value": round(total_value, 2)
    }
    




def get_portfolio_holdings_on_date(portfolio_id, date, user=None):
    portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    if not portfolio:
        raise ValueError("Portfolio not found.")

    if user and portfolio.user != user:
        raise PermissionError("You do not have permission to access this portfolio.")

    if not date:
        raise ValueError("date query parameter is required.")

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    transactions = (
        Transaction.objects
        .select_related("stock")
        .filter(portfolio=portfolio, date__lte=target_date)
        .order_by("date", "id")
    )

    if not transactions.exists():
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "date": target_date,
            "total_value": 0.0,
            "holdings": []
        }

    shares_by_stock = defaultdict(int)

    for txn in transactions:
        if txn.transaction_type == Transaction.BUY:
            shares_by_stock[txn.stock_id] += txn.shares
        elif txn.transaction_type == Transaction.SELL:
            shares_by_stock[txn.stock_id] -= txn.shares

    stock_map = {
        stock.id: stock
        for stock in Stock.objects.filter(id__in=shares_by_stock.keys())
    }

    holdings = []
    total_value = 0.0

    for stock_id, net_shares in shares_by_stock.items():
        if net_shares <= 0:
            continue

        price_obj = (
            HistoricalPrice.objects
            .filter(stock_id=stock_id, date=target_date)
            .first()
        )

        if not price_obj:
            continue

        stock = stock_map.get(stock_id)
        holding_value = net_shares * price_obj.close_price
        total_value += holding_value

        holdings.append({
            "ticker": stock.ticker if stock else "",
            "name": stock.name if stock else "",
            "shares": net_shares,
            "price": round(price_obj.close_price, 2),
            "value": round(holding_value, 2),
        })

    holdings.sort(key=lambda x: x["value"], reverse=True)

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "date": target_date,
        "total_value": round(total_value, 2),
        "holdings": holdings
    }