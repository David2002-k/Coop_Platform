from django.shortcuts import render

from rest_framework import viewsets

from core.permissions import IsAgriculteur

from .models import Cooperative, Production, Produit

from .serializers import (
    CooperativeSerializer,
    ProductionSerializer,
    ProduitSerializer
)

# API Cooperative
class CooperativeViewSet(viewsets.ModelViewSet):
    queryset = Cooperative.objects.all()
    serializer_class = CooperativeSerializer
    permission_classes = [IsAgriculteur]

# API Production
class ProductionViewSet(viewsets.ModelViewSet):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [IsAgriculteur]
    def get_queryset(self):
        user = self.request.user
        return Production.objects.filter(
            membre__utilisateur=user
        )

# API Produit
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [
        IsAgriculteur
    ]