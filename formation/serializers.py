from rest_framework import serializers
from .models import Formation
class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = [
            'id',
            'formateur',
            'titre',
            'description',
            'type_contenu',
            'contenu',
            'duree_estimee',
            'statut'
        ]

#API SuiviFormation
from .models import SuiviFormation
class SuiviFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiviFormation
        fields = [
            'id',
            'membre',
            'formation',
            'progression',
            'score_quiz',
            'statut'
        ]