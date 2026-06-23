"""
Vues web (pages HTML) de la plateforme.

Contrairement aux APIs REST (qui renvoient du JSON), ces vues affichent
de vraies pages navigables avec Bootstrap : connexion, tableau de bord
adapté au rôle, catalogue, et listes personnelles par rôle.
"""
import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Utilisateur, Acheteur
from productions.models import Produit, Production
from sales.models import Commande, LigneCommande, Paiement, Livraison
from formation.models import Formation, SuiviFormation


def accueil(request):
    """Page d'accueil publique."""
    return render(request, 'home.html')


# ---------------------------------------------------------------------
# Inscription web (création d'un compte acheteur)
# ---------------------------------------------------------------------
def inscription(request):
    """Crée un compte acheteur depuis une page web, puis connecte."""
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip().lower()
        mot_passe = request.POST.get('mot_passe', '')
        adresse = request.POST.get('adresse', '').strip()

        if not (nom and prenom and email and mot_passe):
            messages.error(request, "Tous les champs sont obligatoires.")
        elif Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Un compte existe déjà avec cet email.")
        else:
            utilisateur = Utilisateur.objects.create_user(
                email=email, mot_passe=mot_passe, nom=nom, prenom=prenom,
                adresse=adresse, role='ACHETEUR',
            )
            Acheteur.objects.create(
                utilisateur=utilisateur, adresse_livraison=adresse)
            login(request, utilisateur)
            messages.success(request, "Compte créé. Bienvenue !")
            return redirect('catalogue')

    return render(request, 'web/inscription.html')


# ---------------------------------------------------------------------
# Catalogue & panier d'achat (stocké en session)
# ---------------------------------------------------------------------
def catalogue(request):
    """Catalogue public des produits disponibles à la vente."""
    produits = Produit.objects.filter(diponible=True).select_related('production')
    return render(request, 'web/catalogue.html', {'produits': produits})


def _get_panier(request):
    """Retourne le panier (dict {id_produit: quantite}) depuis la session."""
    return request.session.get('panier', {})


def ajouter_au_panier(request, produit_id):
    """Ajoute une unité d'un produit au panier."""
    produit = get_object_or_404(Produit, pk=produit_id)
    panier = _get_panier(request)
    cle = str(produit_id)
    panier[cle] = panier.get(cle, 0) + 1
    request.session['panier'] = panier
    messages.success(request, f"« {produit.nom} » ajouté au panier.")
    return redirect('catalogue')


def retirer_du_panier(request, produit_id):
    """Retire complètement un produit du panier."""
    panier = _get_panier(request)
    panier.pop(str(produit_id), None)
    request.session['panier'] = panier
    return redirect('panier')


def panier(request):
    """Affiche le contenu du panier avec le total."""
    panier_session = _get_panier(request)
    lignes, total = [], Decimal('0')
    for pid, qte in panier_session.items():
        produit = Produit.objects.filter(pk=pid).first()
        if not produit:
            continue
        sous_total = produit.prix_unitaire * qte
        total += sous_total
        lignes.append({'produit': produit, 'quantite': qte,
                       'sous_total': sous_total})
    return render(request, 'web/panier.html', {'lignes': lignes, 'total': total})


@login_required
def valider_commande(request):
    """Transforme le panier en commande payée (+ reçu automatique)."""
    panier_session = _get_panier(request)
    if not panier_session:
        messages.error(request, "Votre panier est vide.")
        return redirect('catalogue')

    # S'assurer que l'utilisateur a un profil acheteur
    acheteur = getattr(request.user, 'acheteur', None)
    if acheteur is None:
        acheteur = Acheteur.objects.create(
            utilisateur=request.user,
            adresse_livraison=request.user.adresse or '')

    with transaction.atomic():
        commande = Commande.objects.create(
            acheteur=acheteur,
            reference="CMD-" + str(uuid.uuid4())[:8].upper(),
            statut="validée",
        )
        total = Decimal('0')
        for pid, qte in panier_session.items():
            produit = Produit.objects.filter(pk=pid).first()
            if not produit:
                continue
            LigneCommande.objects.create(
                commande=commande, produit=produit, quantite=qte,
                prix_unitaire=produit.prix_unitaire,
                sous_total=produit.prix_unitaire * qte)
            total += produit.prix_unitaire * qte
            # Décrémenter le stock
            produit.quantite_stock = max(0, produit.quantite_stock - qte)
            if produit.quantite_stock == 0:
                produit.diponible = False
            produit.save()

        commande.montant_total = total
        commande.save()

        # Paiement (statut payé -> génère automatiquement le reçu)
        Paiement.objects.create(
            commande=commande, montant=total, methode="Mobile Money",
            statut="payé",
            reference_transaction="OM-" + str(uuid.uuid4())[:10].upper())

    request.session['panier'] = {}
    messages.success(request, "Commande validée et payée !")
    return render(request, 'web/commande_confirmee.html',
                  {'commande': commande})


@login_required
def tableau_de_bord(request):
    """Tableau de bord adapté au rôle de l'utilisateur connecté."""
    user = request.user
    contexte = {
        'role': user.role,
        'est_membre': hasattr(user, 'membre'),
        'est_acheteur': hasattr(user, 'acheteur'),
        'est_formateur': hasattr(user, 'formateur'),
        'est_livreur': hasattr(user, 'livreur'),
        'est_admin': user.is_staff,
    }

    # Quelques chiffres utiles selon le rôle
    if contexte['est_membre']:
        contexte['nb_productions'] = Production.objects.filter(
            membre__utilisateur=user).count()
        contexte['nb_formations'] = SuiviFormation.objects.filter(
            membre__utilisateur=user).count()
    if contexte['est_acheteur']:
        contexte['nb_commandes'] = Commande.objects.filter(
            acheteur__utilisateur=user).count()
    if contexte['est_formateur']:
        contexte['nb_formations_creees'] = Formation.objects.filter(
            formateur__utilisateur=user).count()
    if contexte['est_livreur']:
        contexte['nb_livraisons'] = Livraison.objects.filter(
            livreur__utilisateur=user).count()

    return render(request, 'web/tableau_de_bord.html', contexte)


@login_required
def mes_productions(request):
    """Liste des productions de l'agriculteur connecté."""
    productions = Production.objects.filter(membre__utilisateur=request.user)
    return render(request, 'web/mes_productions.html',
                  {'productions': productions})


@login_required
def mes_commandes(request):
    """Liste des commandes de l'acheteur connecté."""
    commandes = Commande.objects.filter(
        acheteur__utilisateur=request.user).order_by('-date_commande')
    return render(request, 'web/mes_commandes.html', {'commandes': commandes})


@login_required
def mes_formations(request):
    """Formations : créées (formateur) ou suivies (membre)."""
    contexte = {}
    if hasattr(request.user, 'formateur'):
        contexte['creees'] = Formation.objects.filter(
            formateur__utilisateur=request.user)
    if hasattr(request.user, 'membre'):
        contexte['suivies'] = SuiviFormation.objects.filter(
            membre__utilisateur=request.user).select_related('formation')
    return render(request, 'web/mes_formations.html', contexte)


@login_required
def mes_livraisons(request):
    """Liste des livraisons affectées au livreur connecté."""
    livraisons = Livraison.objects.filter(
        livreur__utilisateur=request.user).select_related('commande')
    return render(request, 'web/mes_livraisons.html',
                  {'livraisons': livraisons})
