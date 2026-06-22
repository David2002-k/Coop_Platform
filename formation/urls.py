from django.test import TestCase

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FormationViewSet,
    SuiviFormationViewSet
)
router = DefaultRouter()
router.register(
    'formations',
    FormationViewSet
)
router.register(
    'suiviformations',
    SuiviFormationViewSet
)
urlpatterns = [
    path('', include(router.urls))
]
