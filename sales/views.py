from django.shortcuts import render

from rest_framework import viewsets
from .models import (
    Commande,
    LigneCommande,
    Paiement,
    Livraison
)
from .serializers import (
    CommandeSerializer,
    LigneCommandeSerializer,
    PaiementSerializer,
    LivraisonSerializer
)

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer

class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer
