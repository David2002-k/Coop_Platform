from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.permissions import (
    IsFormateur,
    IsAgriculteur
)
from .models import (
    Formation,
    SuiviFormation,
    Quiz
)
from .serializers import (
    FormationSerializer,
    SuiviFormationSerializer,
    QuizSerializer
)

# API Formation
class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    def get_permissions(self):
        # Visiteur + membre peuvent consulter
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Seul formateur crée/modifie
        return [IsFormateur()]

# API SuiviFormation
class SuiviFormationViewSet(viewsets.ModelViewSet):
    queryset = SuiviFormation.objects.all()
    serializer_class = SuiviFormationSerializer
    permission_classes = [IsAgriculteur]
    # rendre les données privées
    def get_queryset(self):
        user = self.request.user
        return SuiviFormation.objects.filter( membre__utilisateur=user)

# API Quiz
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsFormateur]