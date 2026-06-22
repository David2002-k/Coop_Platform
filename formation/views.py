from django.shortcuts import render

from rest_framework import viewsets
#vue Formation
from .models import Formation
from .serializers import FormationSerializer
class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer

#Vue SuiviFormation
from .models import SuiviFormation
from .serializers import SuiviFormationSerializer
class SuiviFormationViewSet(viewsets.ModelViewSet):
    queryset = SuiviFormation.objects.all()
    serializer_class = SuiviFormationSerializer