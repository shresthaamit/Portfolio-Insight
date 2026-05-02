from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.portfolio_risk_service import get_portfolio_risk_analysis
from .services.diversification_service import get_diversification_score
from .serializers import PortfolioRiskSerializer,DiversificationScoreSerializer
from rest_framework.views import APIView

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