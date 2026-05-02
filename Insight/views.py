from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.portfolio_risk_service import get_portfolio_risk_analysis
from .services.diversification_service import get_diversification_score, get_portfolio_vs_benchmark
from .serializers import PortfolioRiskSerializer,DiversificationScoreSerializer,PortfolioBenchmarkComparisonSerializer
from Portfolio.models import Holding, Stock
from rest_framework.permissions import AllowAny
from .services.benchmark_service import generate_benchmark_from_excel
from rest_framework.views import APIView
from Insight.models import MarketBenchmark
# Create your views here.


class PortfolioRiskAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,portfolio_id):
        try:
            data = get_portfolio_risk_analysis(
                portfolio_id=portfolio_id,
                user = request.user
            )
            serializer = PortfolioRiskSerializer(instance = data)
            return Response(serializer.data)
        except  ValueError as e:
            return Response({'detail':'str(e)'}, status = 400)
        
        except PermissionError as e:
            return Response({'detail': str(e)}, status = 403)
        

class DiversificationAPIView(APIView):
    permission_class = [IsAuthenticated]
    def get(self, request, portfolio_id):
        try:
            data = get_diversification_score(portfolio_id=portfolio_id, user=request.user)
            serializer  = DiversificationScoreSerializer(instance = data)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"details":str(e)}, status=400
            )
        except PermissionError as e:
            return Response(
                {"detail":str(e)}, status =403
            )
        


class BenchmarkGenerateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = generate_benchmark_from_excel(
            "./Portfolio/data/Portfolio_data.xlsx"
        )

        return Response({
            "message": "Benchmark generated successfully",
            "total_days": len(data),
            "data": data[:5]  # preview first 5
        })
    
class PortfolioBenchmarkComparisionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            data = get_portfolio_vs_benchmark(portfolio_id= portfolio_id, user = request.user)
            serializer = PortfolioBenchmarkComparisonSerializer(instance = data)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"detail":str(e)},
                status = 400
            )
        except PermissionError as e:
            return Response(
                 {"detail": str(e)},
                status=403
            )
        


class SystemCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "holdings": Holding.objects.count(),
            "stocks": Stock.objects.count(),
            "benchmarks": MarketBenchmark.objects.count()
        })