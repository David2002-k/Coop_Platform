from rest_framework import serializers

from .models import (
    Commande,
    LigneCommande,
    Paiement,
    Livraison
)

# SERIALIZER COMMANDE
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

# SERIALIZER LIGNE COMMANDE
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

# SERIALIZER PAIEMENT
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
# SERIALIZER LIVRAISON
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