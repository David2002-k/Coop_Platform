"""
Commande de génération de données de démonstration.

Usage :
    python manage.py seed_demo

Crée un jeu de données cohérent permettant de tester immédiatement toute
la plateforme : un super-utilisateur, une coopérative, un membre
(agriculteur), un acheteur, un formateur, un livreur, une production
validée, un produit, une formation, une commande payée (avec reçu
généré automatiquement) et une livraison.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import (
    Utilisateur, Membre, Administrateur, Acheteur, Formateur, Livreur,
)
from productions.models import Cooperative, Production, Produit
from formation.models import Formation, SuiviFormation, Quiz
from sales.models import Commande, LigneCommande, Paiement, Livraison


class Command(BaseCommand):
    help = "Crée des données de démonstration cohérentes."

    def handle(self, *args, **options):
        def creer_utilisateur(email, role, nom, prenom, staff=False, sudo=False):
            u, cree = Utilisateur.objects.get_or_create(
                email=email,
                defaults=dict(nom=nom, prenom=prenom, role=role,
                              is_staff=staff or sudo, is_superuser=sudo,
                              telephone='70000000', adresse='Ouagadougou'),
            )
            if cree:
                u.set_password('demo1234')
                u.save()
            return u

        # 1. Super-administrateur
        admin = creer_utilisateur('admin@coop.bf', 'ADMIN', 'Admin',
                                  'Super', sudo=True)

        # 2. Coopérative
        coop, _ = Cooperative.objects.get_or_create(
            nom="Coopérative du Sahel",
            defaults=dict(localisation="Dori", description="Maraîchage"),
        )

        # 3. Administrateur de coopérative
        admin_coop = creer_utilisateur('gestion@coop.bf', 'ADMIN',
                                       'Ouedraogo', 'Awa', staff=True)
        Administrateur.objects.get_or_create(
            utilisateur=admin_coop,
            defaults=dict(cooperative=coop, fonction="Gérante",
                          niveau_acces="TOTAL"),
        )

        # 4. Membre (agriculteur)
        u_membre = creer_utilisateur('membre@coop.bf', 'MEMBRE',
                                     'Sawadogo', 'Issa')
        membre, _ = Membre.objects.get_or_create(
            utilisateur=u_membre,
            defaults=dict(cooperative=coop, numero_adhesion="ADH-001",
                          date_adhesion=timezone.now().date(),
                          statut_cotisation=True,
                          montant_cotisation=Decimal("5000.00")),
        )
        if coop.createur_id is None:
            coop.createur = membre
            coop.save()

        # 5. Acheteur, formateur, livreur
        u_acheteur = creer_utilisateur('acheteur@coop.bf', 'ACHETEUR',
                                       'Kabore', 'Paul')
        acheteur, _ = Acheteur.objects.get_or_create(
            utilisateur=u_acheteur,
            defaults=dict(adresse_livraison="Secteur 15, Ouagadougou"),
        )
        u_formateur = creer_utilisateur('formateur@coop.bf', 'FORMATEUR',
                                        'Traore', 'Fatima')
        formateur, _ = Formateur.objects.get_or_create(
            utilisateur=u_formateur,
            defaults=dict(specialite="Agronomie",
                          biographie="Ingénieure agronome."),
        )
        u_livreur = creer_utilisateur('livreur@coop.bf', 'LIVREUR',
                                      'Compaore', 'Moussa')
        livreur, _ = Livreur.objects.get_or_create(
            utilisateur=u_livreur,
            defaults=dict(vehicule="Tricycle", zone_couverture="Ouagadougou"),
        )

        # 6. Production validée + produit
        production, _ = Production.objects.get_or_create(
            membre=membre, nom="Tomate",
            defaults=dict(type_culture="Maraîchage",
                          quantite=Decimal("300.00"), unite="kg",
                          date_recolte=timezone.now().date(),
                          statut_validation=True),
        )
        produit, _ = Produit.objects.get_or_create(
            production=production, nom="Tomate fraîche",
            defaults=dict(description="Tomates locales",
                          prix_unitaire=Decimal("500.00"),
                          quantite_stock=300, diponible=True),
        )

        # 7. Formation + quiz + suivi
        formation, _ = Formation.objects.get_or_create(
            formateur=formateur, titre="Cultiver la tomate",
            defaults=dict(description="Techniques de maraîchage",
                          type_contenu="COURS", contenu="Chapitre 1...",
                          duree_estimee="2h"),
        )
        Quiz.objects.get_or_create(
            formation=formation,
            question="Quelle saison pour la tomate ?",
            defaults=dict(choix_a="Saison sèche", choix_b="Hivernage",
                          choix_c="Toute l'année", bonne_reponse="A"),
        )
        SuiviFormation.objects.get_or_create(
            membre=membre, formation=formation,
            defaults=dict(progression=Decimal("50.00"), score_quiz=80,
                          statut="EN_COURS"),
        )

        # 8. Commande payée -> reçu auto -> livraison
        commande, _ = Commande.objects.get_or_create(
            reference="CMD-DEMO-001",
            defaults=dict(acheteur=acheteur, montant_total=Decimal("5000.00"),
                          statut="validée"),
        )
        LigneCommande.objects.get_or_create(
            commande=commande, produit=produit,
            defaults=dict(quantite=10, prix_unitaire=Decimal("500.00"),
                          sous_total=Decimal("5000.00")),
        )
        paiement, _ = Paiement.objects.get_or_create(
            commande=commande,
            defaults=dict(montant=Decimal("5000.00"), methode="Mobile Money",
                          statut="payé",
                          reference_transaction="OM-DEMO-001"),
        )
        Livraison.objects.get_or_create(
            commande=commande,
            defaults=dict(livreur=livreur,
                          adresse_livraison=acheteur.adresse_livraison,
                          statut="en préparation"),
        )

        self.stdout.write(self.style.SUCCESS(
            "Données de démonstration créées.\n"
            "Comptes (mot de passe : demo1234) :\n"
            "  admin@coop.bf      (super-admin)\n"
            "  gestion@coop.bf    (administrateur coopérative)\n"
            "  membre@coop.bf     (agriculteur)\n"
            "  acheteur@coop.bf   (acheteur)\n"
            "  formateur@coop.bf  (formateur)\n"
            "  livreur@coop.bf    (livreur)"
        ))
