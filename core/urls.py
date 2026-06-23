"""
URL configuration for core project.

Routage principal de la Plateforme de Gestion des Coopératives Agricoles.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core import web

urlpatterns = [
    # ----- Pages web (interface utilisateur) -----
    path('', web.accueil, name='home'),
    path('catalogue/', web.catalogue, name='catalogue'),
    path('inscription/', web.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='web/connexion.html'), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),
    # Panier d'achat
    path('panier/', web.panier, name='panier'),
    path('panier/ajouter/<int:produit_id>/', web.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/retirer/<int:produit_id>/', web.retirer_du_panier, name='retirer_du_panier'),
    path('panier/valider/', web.valider_commande, name='valider_commande'),
    path('tableau-de-bord/', web.tableau_de_bord, name='tableau_de_bord'),
    path('mes-productions/', web.mes_productions, name='mes_productions'),
    path('mes-commandes/', web.mes_commandes, name='mes_commandes'),
    path('mes-formations/', web.mes_formations, name='mes_formations'),
    path('mes-livraisons/', web.mes_livraisons, name='mes_livraisons'),

    # Interface d'administration Django
    path('admin/', admin.site.urls),

    # Connexion via l'interface navigable de l'API REST
    path('api-auth/', include('rest_framework.urls')),

    # Authentification JWT (connexion par email + mot de passe)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Inscription & profil
    path('api/', include('users.urls')),

    # APIs métier
    path('api/', include('productions.urls')),
    path('api/', include('formation.urls')),
    path('api/', include('sales.urls')),
]

# Service des fichiers téléversés en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
