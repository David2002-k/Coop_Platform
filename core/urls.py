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
    # Paiement MoneyFusion
    path('paiement/retour/', web.paiement_retour, name='paiement_retour'),
    path('paiement/webhook/', web.paiement_webhook, name='paiement_webhook'),
    path('tableau-de-bord/', web.tableau_de_bord, name='tableau_de_bord'),
    # Espace Membre
    path('mes-productions/', web.mes_productions, name='mes_productions'),
    path('declarer-production/', web.declarer_production, name='declarer_production'),
    # Espace Acheteur
    path('mes-commandes/', web.mes_commandes, name='mes_commandes'),
    # Espace Formateur
    path('mes-formations/', web.mes_formations, name='mes_formations'),
    path('creer-formation/', web.creer_formation, name='creer_formation'),
    path('formation/<int:formation_id>/quiz/ajouter/', web.ajouter_quiz, name='ajouter_quiz'),
    # Consultation des formations
    path('formations/', web.liste_formations, name='liste_formations'),
    path('formation/<int:formation_id>/', web.formation_detail, name='formation_detail'),
    path('formation/<int:formation_id>/quiz/passer/', web.passer_quiz, name='passer_quiz'),
    # Espace Livreur
    path('mes-livraisons/', web.mes_livraisons, name='mes_livraisons'),
    path('livraison/<int:livraison_id>/statut/', web.changer_statut_livraison,
         name='changer_statut_livraison'),
    # Espace Administrateur (gestion de la coopérative)
    path('gestion/', web.gestion, name='gestion'),
    path('gestion/productions/', web.gestion_productions, name='gestion_productions'),
    path('gestion/productions/<int:production_id>/valider/',
         web.valider_production, name='valider_production'),
    path('gestion/membres/', web.gestion_membres, name='gestion_membres'),
    path('gestion/produits/', web.gestion_produits, name='gestion_produits'),
    path('gestion/produits/<int:produit_id>/toggle/', web.produit_toggle, name='produit_toggle'),
    path('gestion/produits/<int:produit_id>/supprimer/', web.produit_supprimer, name='produit_supprimer'),

    # Interface d'administration Django (technique)
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
