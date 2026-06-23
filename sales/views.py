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
    Livraison,
    Recu
)
from .serializers import (
    CommandeSerializer,
    LigneCommandeSerializer,
    PaiementSerializer,
    LivraisonSerializer,
    RecuSerializer
)

# API Commande
class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [IsAcheteur]
    #rendre les données privé
    def get_queryset(self):
        user = self.request.user
        return Commande.objects.filter(acheteur__utilisateur=user)

# API LigneCommande
class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer
    permission_classes = [IsAcheteur]
    #rendre les données privé
    def get_queryset(self):
        user = self.request.user
        return LigneCommande.objects.filter(commande__acheteur__utilisateur=user)

# API Paiement
class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [IsAcheteur]
    #rendre les données privé
    def get_queryset(self):
        user = self.request.user
        return Paiement.objects.filter(commande__acheteur__utilisateur=user)

# API Livraison
class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer
    permission_classes = [IsLivreur]
    #rendre les données privé
    def get_queryset(self):
        user = self.request.user
        return Livraison.objects.filter(livreur__utilisateur=user)
    
#Api Reçu
class RecuViewSet(viewsets.ModelViewSet):
    queryset = Recu.objects.all()
    serializer_class = RecuSerializer
    permission_classes = [IsAcheteur]
    def get_queryset(self):
        user = self.request.user
        return Recu.objects.filter(paiement__commande__acheteur__utilisateur=user)