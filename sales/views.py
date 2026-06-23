from django.shortcuts import render

from rest_framework import viewsets

from core.permissions import (
    IsAcheteur,
    IsLivreur
)
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

# API Commande
class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [IsAcheteur]

# API LigneCommande
class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer
    permission_classes = [IsAcheteur]

# API Paiement
class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [IsAcheteur]

# API Livraison
class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer
    permission_classes = [IsLivreur]