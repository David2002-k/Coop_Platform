"""creation d'une API qui permet :
Un agriculteur crée une coopérative
L'API reçoit les données
Django enregistre dans PostgreSQL
L'API retourne un JSON """

from rest_framework import serializers
from .models import Cooperative

class CooperativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperative
        fields = [
            'id',
            'nom',
            'description',
            'localisation',
            'createur',
            'date_creation',
            'statut'
        ]
#creation de l'api production
from .models import Production
class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = [
            'id',
            'membre',
            'nom',
            'type_culture',
            'quantite',
            'unite',
            'date_recolte',
            'statut_validation'
        ]

#creation de l'api produit
from .models import Produit
class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = [
            'id',
            'production',
            'nom',
            'description',
            'prix_unitaire',
            'quantite_stock',
            'diponible',
            'image'
        ]
