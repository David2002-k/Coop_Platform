from rest_framework import serializers

from .models import (
    Commande,
    LigneCommande,
    Paiement,
    Livraison,
    Recu
)

# Serializer Commande
class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = [
            'id',
            'acheteur',
            'reference',
            'date_commande',
            'montant_total',
            'statut'
        ]

# Serializer Ligne Commande
class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = [
            'id',
            'commande',
            'produit',
            'quantite',
            'prix_unitaire',
            'sous_total'
        ]

# Serializer Paiement
class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = [
            'id',
            'commande',
            'montant',
            'methode',
            'statut',
            'date_paiement',
            'reference_transaction'
        ]
# Serializer Livraison
class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = [
            'id',
            'commande',
            'livreur',
            'adresse_livraison',
            'date_livraison',
            'statut'
        ]

#Serializer Reçu
from .models import Recu
class RecuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recu
        fields = "__all__"