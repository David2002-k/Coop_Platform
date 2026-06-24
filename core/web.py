"""
Vues web (pages HTML) de la plateforme.

Contrairement aux APIs REST (qui renvoient du JSON), ces vues affichent
de vraies pages navigables avec Bootstrap : connexion, tableau de bord
adapté au rôle, catalogue, et listes personnelles par rôle.
"""
import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from users.models import Utilisateur, Acheteur, Membre, Administrateur
from productions.models import Produit, Production, Cooperative
from sales.models import Commande, LigneCommande, Paiement, Livraison
from formation.models import Formation, SuiviFormation, Quiz


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
    """Catalogue public des produits disponibles, avec recherche."""
    recherche = request.GET.get('q', '').strip()
    produits = Produit.objects.filter(diponible=True).select_related('production')
    if recherche:
        produits = produits.filter(nom__icontains=recherche)
    return render(request, 'web/catalogue.html',
                  {'produits': produits, 'recherche': recherche})


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


def _confirmer_commande(commande):
    """
    Marque une commande comme payée : décrémente le stock et passe le
    paiement à « payé » (ce qui génère automatiquement le reçu).
    Idempotent : ne fait rien si la commande est déjà payée.
    """
    paiement = getattr(commande, 'paiement', None)
    if paiement and paiement.statut == 'payé':
        return  # déjà confirmée

    with transaction.atomic():
        for ligne in commande.lignecommande_set.all():
            produit = ligne.produit
            produit.quantite_stock = max(0, produit.quantite_stock - ligne.quantite)
            if produit.quantite_stock == 0:
                produit.diponible = False
            produit.save()
        commande.statut = 'payée'
        commande.save()
        if paiement:
            paiement.statut = 'payé'
            paiement.save()  # déclenche la création du reçu


@login_required
def valider_commande(request):
    """
    Crée la commande à partir du panier puis lance le paiement.

    - Si MoneyFusion est configuré (.env) : redirige vers la page de
      paiement Mobile Money réelle.
    - Sinon (développement) : valide immédiatement (mode simulation).
    """
    from sales import moneyfusion
    from django.urls import reverse

    panier_session = _get_panier(request)
    if not panier_session:
        messages.error(request, "Votre panier est vide.")
        return redirect('catalogue')

    numero = request.POST.get('numero', '').strip()

    # Profil acheteur (créé à la volée si nécessaire)
    acheteur = getattr(request.user, 'acheteur', None)
    if acheteur is None:
        acheteur = Acheteur.objects.create(
            utilisateur=request.user,
            adresse_livraison=request.user.adresse or '')

    # Création de la commande « en attente » + lignes
    with transaction.atomic():
        commande = Commande.objects.create(
            acheteur=acheteur,
            reference="CMD-" + str(uuid.uuid4())[:8].upper(),
            statut="en attente",
        )
        total = Decimal('0')
        articles = []
        for pid, qte in panier_session.items():
            produit = Produit.objects.filter(pk=pid).first()
            if not produit:
                continue
            LigneCommande.objects.create(
                commande=commande, produit=produit, quantite=qte,
                prix_unitaire=produit.prix_unitaire,
                sous_total=produit.prix_unitaire * qte)
            total += produit.prix_unitaire * qte
            articles.append({produit.nom: float(produit.prix_unitaire * qte)})
        commande.montant_total = total
        commande.save()

    # ----- Mode simulation (pas de MoneyFusion configuré) -----
    if not moneyfusion.est_configure():
        Paiement.objects.create(
            commande=commande, montant=total, methode="Mobile Money",
            statut="en attente",
            reference_transaction="MM-" + str(uuid.uuid4())[:10].upper())
        _confirmer_commande(commande)
        request.session['panier'] = {}
        messages.success(request, "Commande validée et payée (mode simulation).")
        return render(request, 'web/commande_confirmee.html',
                      {'commande': commande, 'simulation': True})

    # ----- Mode réel : appel à MoneyFusion -----
    return_url = settings.SITE_URL + reverse('paiement_retour')
    webhook_url = settings.SITE_URL + reverse('paiement_webhook')
    try:
        resultat = moneyfusion.initier_paiement(
            total=total,
            nom_client=f"{request.user.prenom} {request.user.nom}",
            numero=numero,
            articles=articles,
            return_url=return_url,
            webhook_url=webhook_url,
            infos=[{"reference": commande.reference}],
        )
    except Exception as exc:  # réseau / API indisponible
        commande.statut = "échec"
        commande.save()
        messages.error(request, f"Le service de paiement est indisponible : {exc}")
        return redirect('panier')

    if not resultat.get('statut') or not resultat.get('url'):
        commande.statut = "échec"
        commande.save()
        messages.error(request, resultat.get('message', "Paiement refusé."))
        return redirect('panier')

    token = resultat.get('token', '')
    Paiement.objects.create(
        commande=commande, montant=total, methode="Mobile Money",
        statut="en attente",
        reference_transaction=token or ("MF-" + str(uuid.uuid4())[:10]))
    # On mémorise le token pour la page de retour
    request.session['paiement_token'] = token
    request.session['panier'] = {}
    # Redirection vers la page de paiement MoneyFusion
    return redirect(resultat['url'])


def paiement_retour(request):
    """
    Page de retour après paiement MoneyFusion (return_url).
    Vérifie le statut réel du paiement et confirme la commande.
    """
    from sales import moneyfusion
    token = (request.GET.get('token')
             or request.session.get('paiement_token', ''))
    paiement = Paiement.objects.filter(reference_transaction=token).first()
    if not paiement:
        messages.error(request, "Paiement introuvable.")
        return redirect('catalogue')

    try:
        resultat = moneyfusion.verifier_paiement(token)
    except Exception:
        messages.warning(request, "Vérification en cours, réessayez plus tard.")
        return redirect('mes_commandes')

    if moneyfusion.est_paye(resultat):
        _confirmer_commande(paiement.commande)
        request.session.pop('paiement_token', None)
        return render(request, 'web/commande_confirmee.html',
                      {'commande': paiement.commande})

    return render(request, 'web/paiement_echec.html',
                  {'commande': paiement.commande})


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


@csrf_exempt
@require_POST
def paiement_webhook(request):
    """
    Endpoint appelé par MoneyFusion pour notifier l'état d'un paiement.
    Vérifie le statut et confirme la commande si payée.
    """
    from sales import moneyfusion
    try:
        donnees = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        donnees = {}

    token = (donnees.get('tokenPay') or donnees.get('token')
             or request.GET.get('token', ''))
    paiement = Paiement.objects.filter(reference_transaction=token).first()
    if not paiement:
        return JsonResponse({'ok': False, 'message': 'paiement introuvable'},
                            status=404)

    try:
        resultat = moneyfusion.verifier_paiement(token)
    except Exception:
        resultat = donnees  # à défaut, on se fie à la charge utile reçue

    if moneyfusion.est_paye(resultat):
        _confirmer_commande(paiement.commande)

    return JsonResponse({'ok': True})


# =====================================================================
#  ESPACE MEMBRE (AGRICULTEUR)
# =====================================================================
@login_required
def declarer_production(request):
    """Le membre déclare une nouvelle récolte (en attente de validation)."""
    membre = getattr(request.user, 'membre', None)
    if membre is None:
        messages.error(request, "Seuls les membres peuvent déclarer une production.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        Production.objects.create(
            membre=membre,
            nom=request.POST.get('nom', '').strip(),
            type_culture=request.POST.get('type_culture', '').strip(),
            quantite=request.POST.get('quantite') or 0,
            unite=request.POST.get('unite', 'kg').strip(),
            date_recolte=request.POST.get('date_recolte') or timezone.now().date(),
            statut_validation=False,
        )
        messages.success(request, "Production déclarée. Elle sera validée par un administrateur.")
        return redirect('mes_productions')

    return render(request, 'web/declarer_production.html')


# =====================================================================
#  ESPACE FORMATEUR
# =====================================================================
@login_required
def creer_formation(request):
    """Le formateur publie une nouvelle formation."""
    formateur = getattr(request.user, 'formateur', None)
    if formateur is None:
        messages.error(request, "Seuls les formateurs peuvent créer une formation.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        formation = Formation.objects.create(
            formateur=formateur,
            titre=request.POST.get('titre', '').strip(),
            description=request.POST.get('description', '').strip(),
            type_contenu=request.POST.get('type_contenu', 'COURS'),
            contenu=request.POST.get('contenu', '').strip(),
            duree_estimee=request.POST.get('duree_estimee', '').strip(),
            fichier=request.FILES.get('fichier'),
        )
        messages.success(request, "Formation publiée. Vous pouvez y ajouter un quiz.")
        return redirect('ajouter_quiz', formation_id=formation.id)

    return render(request, 'web/creer_formation.html',
                  {'types': Formation.TYPE_CONTENU})


@login_required
def ajouter_quiz(request, formation_id):
    """Le formateur ajoute des questions de quiz à sa formation."""
    formation = get_object_or_404(
        Formation, pk=formation_id, formateur__utilisateur=request.user)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            Quiz.objects.create(
                formation=formation,
                question=question,
                choix_a=request.POST.get('choix_a', '').strip(),
                choix_b=request.POST.get('choix_b', '').strip(),
                choix_c=request.POST.get('choix_c', '').strip(),
                bonne_reponse=request.POST.get('bonne_reponse', 'A').strip().upper()[:1],
            )
            messages.success(request, "Question ajoutée.")
        return redirect('ajouter_quiz', formation_id=formation.id)

    return render(request, 'web/ajouter_quiz.html', {
        'formation': formation,
        'questions': formation.quiz_set.all(),
    })


# =====================================================================
#  CONSULTATION DES FORMATIONS (membres / public connecté)
# =====================================================================
@login_required
def liste_formations(request):
    """Catalogue des formations disponibles."""
    formations = Formation.objects.select_related('formateur__utilisateur')
    return render(request, 'web/formations_liste.html', {'formations': formations})


def _video_embed(url):
    """Transforme un lien YouTube/Vimeo en URL d'intégration (iframe)."""
    if not url:
        return None
    url = url.strip()
    if 'youtube.com/watch?v=' in url:
        ident = url.split('watch?v=')[1].split('&')[0]
        return f'https://www.youtube-nocookie.com/embed/{ident}'
    if 'youtu.be/' in url:
        ident = url.split('youtu.be/')[1].split('?')[0]
        return f'https://www.youtube-nocookie.com/embed/{ident}'
    if 'vimeo.com/' in url and 'player.' not in url:
        ident = url.rstrip('/').split('/')[-1]
        return f'https://player.vimeo.com/video/{ident}'
    return None


@login_required
def formation_detail(request, formation_id):
    """Page d'une formation : contenu, vidéo, PDF téléchargeable, quiz."""
    formation = get_object_or_404(Formation, pk=formation_id)
    questions = formation.quiz_set.all()
    suivi = None
    membre = getattr(request.user, 'membre', None)
    if membre:
        suivi = SuiviFormation.objects.filter(
            membre=membre, formation=formation).first()
    return render(request, 'web/formation_detail.html', {
        'formation': formation,
        'questions': questions,
        'suivi': suivi,
        'est_membre': membre is not None,
        'video_embed': _video_embed(formation.contenu),
    })


@login_required
@require_POST
def passer_quiz(request, formation_id):
    """Le membre répond au quiz ; le score est calculé et enregistré."""
    formation = get_object_or_404(Formation, pk=formation_id)
    membre = getattr(request.user, 'membre', None)
    if membre is None:
        messages.error(request, "Seuls les membres peuvent passer le quiz.")
        return redirect('formation_detail', formation_id=formation.id)

    questions = list(formation.quiz_set.all())
    if not questions:
        messages.info(request, "Cette formation n'a pas encore de quiz.")
        return redirect('formation_detail', formation_id=formation.id)

    bonnes = 0
    for q in questions:
        reponse = request.POST.get(f'q{q.id}', '').strip().upper()
        if reponse == q.bonne_reponse.upper():
            bonnes += 1
    score = round(100 * bonnes / len(questions), 2)

    suivi, _ = SuiviFormation.objects.get_or_create(
        membre=membre, formation=formation,
        defaults={'progression': 0, 'score_quiz': 0, 'statut': 'EN_COURS'})
    suivi.score_quiz = int(score)
    suivi.progression = 100
    suivi.statut = 'TERMINEE'
    suivi.save()

    messages.success(
        request, f"Quiz terminé : {bonnes}/{len(questions)} bonnes réponses "
                 f"({score} %).")
    return redirect('formation_detail', formation_id=formation.id)


# =====================================================================
#  ESPACE LIVREUR
# =====================================================================
@login_required
@require_POST
def changer_statut_livraison(request, livraison_id):
    """Le livreur fait avancer le statut d'une livraison."""
    livraison = get_object_or_404(
        Livraison, pk=livraison_id, livreur__utilisateur=request.user)
    nouveau = request.POST.get('statut', '')
    valides = ["en préparation", "en cours", "livrée"]
    if nouveau in valides:
        livraison.statut = nouveau
        if nouveau == "livrée":
            livraison.date_livraison = timezone.now()
        livraison.save()
        messages.success(request, f"Livraison mise à jour : {nouveau}.")
    return redirect('mes_livraisons')


# =====================================================================
#  ESPACE ADMINISTRATEUR (niveaux d'accès)
# =====================================================================
def _profil_admin(user):
    """Retourne (profil_admin, niveau). Le superutilisateur a tous les droits."""
    profil = getattr(user, 'administrateur', None)
    return profil


def _admin_peut_gerer(user):
    if user.is_superuser:
        return True
    profil = getattr(user, 'administrateur', None)
    return bool(profil and profil.peut_gerer)


@login_required
def gestion(request):
    """Tableau de bord d'administration de la coopérative."""
    if not (request.user.is_staff or hasattr(request.user, 'administrateur')):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('tableau_de_bord')

    import json as _json
    from collections import OrderedDict

    profil = getattr(request.user, 'administrateur', None)
    payees = Commande.objects.filter(statut='payée')

    # --- Ventes des 6 derniers mois (graphique en ligne) ---
    aujourd = timezone.now()
    mois_labels, mois_valeurs = [], []
    noms_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    for i in range(5, -1, -1):
        annee = aujourd.year
        mois = aujourd.month - i
        while mois <= 0:
            mois += 12
            annee -= 1
        total = sum(c.montant_total for c in payees.filter(
            date_commande__year=annee, date_commande__month=mois))
        mois_labels.append(noms_mois[mois - 1])
        mois_valeurs.append(float(total))

    # --- Répartition des commandes par statut (graphique camembert) ---
    statuts = OrderedDict()
    for c in Commande.objects.all():
        statuts[c.statut] = statuts.get(c.statut, 0) + 1

    # --- Top 5 des produits les plus commandés ---
    top = {}
    for l in LigneCommande.objects.select_related('produit'):
        top[l.produit.nom] = top.get(l.produit.nom, 0) + l.quantite
    top_tries = sorted(top.items(), key=lambda x: x[1], reverse=True)[:5]

    contexte = {
        'rubrique': 'tableau',
        'profil': profil,
        'niveau': profil.get_niveau_acces_display() if profil else "Accès total",
        'peut_gerer': _admin_peut_gerer(request.user),
        'nb_membres': Membre.objects.count(),
        'nb_productions_attente': Production.objects.filter(statut_validation=False).count(),
        'nb_produits': Produit.objects.count(),
        'nb_commandes': Commande.objects.count(),
        'total_ventes': sum(c.montant_total for c in payees),
        # Données JSON pour les graphiques
        'ventes_labels': _json.dumps(mois_labels),
        'ventes_valeurs': _json.dumps(mois_valeurs),
        'statuts_labels': _json.dumps(list(statuts.keys())),
        'statuts_valeurs': _json.dumps(list(statuts.values())),
        'top_labels': _json.dumps([t[0] for t in top_tries]),
        'top_valeurs': _json.dumps([float(t[1]) for t in top_tries]),
    }
    return render(request, 'web/gestion/tableau.html', contexte)


@login_required
def gestion_productions(request):
    """Liste des productions à valider."""
    if not (request.user.is_staff or hasattr(request.user, 'administrateur')):
        return redirect('tableau_de_bord')
    productions = Production.objects.select_related('membre__utilisateur').order_by(
        'statut_validation', '-id')
    return render(request, 'web/gestion/productions.html', {
        'rubrique': 'productions',
        'productions': productions,
        'peut_gerer': _admin_peut_gerer(request.user),
    })


@login_required
@require_POST
def valider_production(request, production_id):
    """
    Valide une production et la publie au catalogue (création du produit).
    C'est le lien entre la récolte déclarée et le produit vendable.
    """
    if not _admin_peut_gerer(request.user):
        messages.error(request, "Votre niveau d'accès ne permet pas cette action.")
        return redirect('gestion_productions')

    production = get_object_or_404(Production, pk=production_id)
    production.statut_validation = True
    production.save()

    prix = request.POST.get('prix_unitaire') or 0
    if not Produit.objects.filter(production=production).exists():
        Produit.objects.create(
            production=production,
            nom=production.nom,
            description=f"{production.type_culture} — récolte du {production.date_recolte}",
            prix_unitaire=prix,
            quantite_stock=int(float(production.quantite or 0)),
            diponible=True,
        )
    messages.success(request, f"Production « {production.nom} » validée et publiée au catalogue.")
    return redirect('gestion_productions')


@login_required
def gestion_membres(request):
    """Liste des membres de la coopérative."""
    if not (request.user.is_staff or hasattr(request.user, 'administrateur')):
        return redirect('tableau_de_bord')
    membres = Membre.objects.select_related('utilisateur', 'cooperative')
    return render(request, 'web/gestion/membres.html',
                  {'rubrique': 'membres', 'membres': membres})
