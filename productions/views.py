from django.shortcuts import render
from rest_framework import viewsets
#vue de l'api cooperative
from .models import Cooperative
from .serializers import CooperativeSerializer
class CooperativeViewSet(viewsets.ModelViewSet):
    queryset = Cooperative.objects.all()
    serializer_class = CooperativeSerializer

#vue de l'api produit
from .models import Production
from .serializers import ProductionSerializer
class ProductionViewSet(viewsets.ModelViewSet):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer

# vue de l'api produit
from .models import Produit
from .serializers import ProduitSerializer
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
