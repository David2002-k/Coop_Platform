from django.test import TestCase
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CooperativeViewSet,
    ProductionViewSet,
    ProduitViewSet
)
# Création du routeur API
router = DefaultRouter()
# API Cooperative
router.register(
    'cooperatives',
    CooperativeViewSet
)
# API Production
router.register(
    'productions',
    ProductionViewSet
)
# API Produit
router.register(
    'produits',
    ProduitViewSet
)
urlpatterns = [
    path('',include(router.urls)
    )
]