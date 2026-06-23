from django.urls import path

from .views import RegisterView, MeView

urlpatterns = [
    # Inscription d'un nouvel utilisateur
    path('register/', RegisterView.as_view(), name='register'),
    # Profil de l'utilisateur connecté
    path('me/', MeView.as_view(), name='me'),
]
