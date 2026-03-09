from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from django.db import transaction as db_transaction

from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http import HttpResponse, JsonResponse
from .models import HistoricalPrice,Stock,Portfolio,Transaction, Holding
from .serializers import (MarketHistorySerializer,MarketLatestSerializer,
                          MarketSeriesPointSerializer, StockMetaSerializer,
                          PortfolioSerializer,TransactionSerializer, BuyTransactionSerializer, SellTransactionSerializer,HoldingSerializer
                          
                          )
from .services import load_market_full
def LoadMarketDataView(request):
    result = load_market_full('./Portfolio/data/Portfolio_data.xlsx')
    return JsonResponse(result)


class MarketHistoryView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "symbol is required"}, status=status.HTTP_400_BAD_REQUEST)
        symbol = symbol.strip().upper()
        from_str = request.query_params.get("from")
        to_str = request.query_params.get("to")
        from_date = parse_date(from_str) if from_str else None
        to_date = parse_date(to_str) if to_str else None
        if from_str and not from_date:
            return Response({"error": "Invalid from date. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        if to_str and not to_date:
            return Response({"error": "Invalid to date. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            HistoricalPrice.objects
            .select_related("stock")
            .filter(stock__ticker=symbol)
            .order_by("date")
        )
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)
        data = MarketHistorySerializer(qs,many=True).data
        return Response({
            "symbol":symbol,
            "count": len(data),
            "from": from_str,
            "to": to_str,
            "data": data
        })

class MarketLatestView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "symbol is required"}, status=status.HTTP_400_BAD_REQUEST)

        symbol = symbol.strip().upper()
        latest = (
            HistoricalPrice.objects
            .select_related("stock")
            .filter(stock__ticker = symbol)
            .order_by("-date")
            .first()
        )
        if not latest:
            return Response({"error":f"No data found for symbol {symbol}"}, status=status.HTTP_404_NOT_FOUND)
        return Response(MarketLatestSerializer(latest).data)

class MarketSeriesView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        symbol =  request.query_params.get("symbol")
        if not symbol:
            return Response({"error":"symbols are required"}, status =status.HTTP_400_BAD_REQUEST)
        symbol = symbol.strip().upper()
        from_str  = request.query_params.get("from")
        to_str = request.query_params.get("to")
        from_date = parse_date(from_str) if from_str else None
        to_date = parse_date(to_str) if to_str else None

        if from_str and not from_date:
            return Response({"error":"Invalid from date. Use YYYY-MM-DD"}, status= status.HTTP_400_BAD_REQUEST)
        
        if to_str and not to_date:
            return Response({"error":"Invalid from date. Use YYYY-MM-DD"}, status= status.HTTP_400_BAD_REQUEST)

        qs = (
            HistoricalPrice.objects
            .filter(stock__ticker = symbol)
            .order_by("date")
            .only("date","close_price","stock_id")

        )
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)

        data  = MarketSeriesPointSerializer(qs, many=True).data
        return Response({"symbol":symbol,"count":len(data),"data":data})
    
class MarketSymbolView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        q = request.query_params.get("q")
        qs = Stock.objects.all().order_by("ticker").values_list("ticker", flat=True)
        if q:
            q= q.strip().upper()
            qs= qs.filter(ticker__icontains=q)
        return Response(list(qs))

class MarketStocksView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get("q")

        qs = Stock.objects.filter(
            name__isnull=False,
            sector__isnull=False
        ).exclude(name="").exclude(sector="").order_by("ticker")

        if q:
            q = q.strip().upper()
            qs = qs.filter(ticker__istartswith=q)

        return Response(StockMetaSerializer(qs, many=True).data)
    

class PortfolioListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        qs = Portfolio.objects.filter(user=request.user).order_by("-created_at")
        return Response(PortfolioSerializer(qs, many=True).data)

    def post(self,request):
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(user = request.user)
            return Response(PortfolioSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ticker = request.query_params.get("ticker")
        date_str = request.query_params.get("date")

        if not ticker:
            return Response({"error": "ticker is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not date_str:
            return Response({"error": "date is required"}, status=status.HTTP_400_BAD_REQUEST)

        parsed_date = parse_date(date_str)
        if not parsed_date:
            return Response({"error": "Invalid date. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        ticker = ticker.strip().upper()

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            historical_price = HistoricalPrice.objects.get(stock=stock, date=parsed_date)
        except HistoricalPrice.DoesNotExist:
            return Response(
                {"error": "No historical price found for selected stock on this date"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "ticker": stock.ticker,
            "name": stock.name,
            "date": parsed_date,
            "price": historical_price.close_price
        })
    

class BuyTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        serializer = BuyTransactionSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        portfolio = serializer.validated_data["portfolio"]
        stock = serializer.validated_data["stock"]
        buy_date = serializer.validated_data["date"]
        shares = serializer.validated_data["shares"]
        historical_price = serializer.validated_data["historical_price"]
        price = historical_price.close_price

        buy_txn = Transaction.objects.create(
            portfolio=portfolio,
            stock=stock,
            transaction_type=Transaction.BUY,
            date=buy_date,
            shares=shares,
            price=price
        )

        holding, created = Holding.objects.get_or_create(
            portfolio=portfolio,
            stock=stock,
            defaults={
                "shares": shares,
                "purchase_price": price,
                "purchase_date": buy_date
            }
        )

        if not created:
            total_cost = (holding.shares * holding.purchase_price) + (shares * price)
            total_shares = holding.shares + shares

            holding.shares = total_shares
            holding.purchase_price = total_cost / total_shares
            holding.purchase_date = buy_date
            holding.save()

        return Response(
            {
                "message": "BUY transaction created successfully",
                "transaction": TransactionSerializer(buy_txn).data,
                "holding": {
                    "ticker": holding.stock.ticker,
                    "shares": holding.shares,
                    "average_price": holding.purchase_price,
                    "purchase_date": holding.purchase_date
                }
            },
            status=status.HTTP_201_CREATED
        )
    


class SellTransactionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SellTransactionSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        portfolio = serializer.validated_data["portfolio"]
        stock = serializer.validated_data["stock"]
        shares = serializer.validated_data["shares"]
        date = serializer.validated_data["date"]
        price = serializer.validated_data["price"]
        holding = serializer.validated_data["holding"]
        transaction = Transaction.objects.create(
            portfolio=portfolio,
            stock = stock,
            transaction_type="SELL",
            date=date,
            shares=shares,
            price=price
        )
        holding.shares -= shares
        if holding.shares == 0:
            holding.delete()

        else:
            holding.save()

        return Response({
            "message": "SELL transaction successful",
            "transaction": TransactionSerializer(transaction).data
        }, status=201)           
class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")

        qs = (
            Transaction.objects
            .filter(portfolio__user=request.user)
            .select_related("portfolio", "stock")
            .order_by("date", "id")
        )

        if portfolio_id:
            qs = qs.filter(portfolio_id=portfolio_id)

        serializer = TransactionSerializer(qs, many=True)

        total_investment = sum(t.total_amount for t in qs if t.transaction_type == "BUY")

        return Response( {"transactions": serializer.data,
            "total": total_investment})
    

class HoldingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")

        if not portfolio_id:
            return Response(
                {"error": "portfolio_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"error": "Portfolio not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        qs = Holding.objects.filter(
            portfolio=portfolio
        ).select_related("stock").order_by("stock__ticker")

        return Response(HoldingSerializer(qs, many=True).data)

def sample_view(request):
    data = []
    sample = HistoricalPrice.objects.order_by('?')[:10]

    for p in sample:
        data.append({
            "symbol": p.stock.ticker,
            "date": p.date,
            "close": p.close_price,
            "volume": p.volume
        })

    return JsonResponse(data, safe=False)


