from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UtilisateurSerializer


class RegisterView(generics.CreateAPIView):
    """
    Inscription publique d'un nouvel utilisateur.
    POST /api/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """
    Renvoie le profil de l'utilisateur actuellement connecté.
    GET /api/me/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = UtilisateurSerializer(request.user).data
        # On indique quels profils spécialisés existent
        data['profils'] = {
            'membre': hasattr(request.user, 'membre'),
            'administrateur': hasattr(request.user, 'administrateur'),
            'acheteur': hasattr(request.user, 'acheteur'),
            'formateur': hasattr(request.user, 'formateur'),
            'livreur': hasattr(request.user, 'livreur'),
        }
        return Response(data, status=status.HTTP_200_OK)
