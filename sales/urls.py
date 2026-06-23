
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommandeViewSet,
    LigneCommandeViewSet,
    PaiementViewSet,
    LivraisonViewSet,
    RecuViewSet
)
router = DefaultRouter()
router.register(
    'commandes',
    CommandeViewSet
)
router.register(
    'lignes-commandes',
    LigneCommandeViewSet
)
router.register(
    'paiements',
    PaiementViewSet
)
router.register(
    'livraisons',
    LivraisonViewSet
)
router.register(
    'recus',
    RecuViewSet
)
urlpatterns = [
    path('',include(router.urls))
]
