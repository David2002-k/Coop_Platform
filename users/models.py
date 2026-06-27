from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class UtilisateurManager(BaseUserManager):
    """
    Gestionnaire (manager) du modèle Utilisateur.

    C'est lui qui sait créer correctement un compte : il normalise
    l'email et hash le mot de passe avant de l'enregistrer en base
    (jamais de mot de passe en clair).
    """

    def create_user(self, email, mot_passe=None, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        utilisateur = self.model(email=email, **extra_fields)
        # On accepte « mot_passe » (français) ou « password » (Django)
        utilisateur.set_password(password or mot_passe)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, mot_passe=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('nom', 'Admin')
        extra_fields.setdefault('prenom', 'Super')
        return self.create_user(email, mot_passe, password, **extra_fields)


"""
 TABLE : UTILISATEUR
 Compte de connexion commun à tous les acteurs de la plateforme :
 Administrateur, Agriculteur/Membre, Acheteur, Formateur, Livreur.

 Ce modèle EST le modèle d'authentification de Django
 (AUTH_USER_MODEL = 'users.Utilisateur'). La connexion se fait par
 email + mot de passe ; le champ « role » indique quel profil
 spécialisé consulter (membre, administrateur, etc.).
"""
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    # Les différents types d'utilisateurs du système
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('MEMBRE', 'Membre'),
        ('ACHETEUR', 'Acheteur'),
        ('FORMATEUR', 'Formateur'),
        ('LIVREUR', 'Livreur'),
    ]

    # Nom de l'utilisateur
    nom = models.CharField(max_length=80)
    # Prénom de l'utilisateur
    prenom = models.CharField(max_length=80)
    # Email utilisé pour la connexion (identifiant unique)
    email = models.EmailField(unique=True)
    # Numéro de téléphone
    telephone = models.CharField(max_length=50, blank=True)
    # Adresse de l'utilisateur
    adresse = models.CharField(max_length=255, blank=True)
    # Permet d'identifier le type d'utilisateur
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBRE'
    )
    # Permet de désactiver un compte sans le supprimer (champ « actif »)
    is_active = models.BooleanField(default=True)
    # Accès à l'interface d'administration Django
    is_staff = models.BooleanField(default=False)
    # Date d'inscription
    date_inscription = models.DateTimeField(auto_now_add=True)

    # Le mot de passe (« mot_passe » dans le schéma) est géré et hashé
    # par AbstractBaseUser via le champ « password ».

    objects = UtilisateurManager()

    # Champ utilisé pour se connecter
    USERNAME_FIELD = 'email'
    # Champs demandés en plus lors d'un createsuperuser
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    # Alias pratique : « actif » comme dans le cahier des charges
    @property
    def actif(self):
        return self.is_active

    # Affichage lisible dans l'administration Django
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role}) ({self.email})"

"""
 TABLE : MEMBRE
 Représente un agriculteur appartenant à une coopérative
 Relation :
 Un utilisateur possède un profil membre
 Un membre appartient à une coopérative
"""
class Membre(models.Model):
    # Relation 1-1 avec Utilisateur
    # Un utilisateur ne peut avoir qu'un seul profil membre
    utilisateur = models.OneToOneField(
        Utilisateur,
        primary_key=True,
        on_delete=models.CASCADE
    )
    # La coopérative à laquelle appartient l'agriculteur
    cooperative = models.ForeignKey(
        'productions.Cooperative',
        on_delete=models.CASCADE
    )
    # Numéro donné lors de l'adhésion
    numero_adhesion = models.CharField(max_length=30)
    # Date d'entrée dans la coopérative
    date_adhesion = models.DateField()
    # Indique si la cotisation est payée
    statut_cotisation = models.BooleanField(default=False)
    # Montant payé par le membre
    montant_cotisation = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom}"


"""
 TABLE : ADMINISTRATEUR
 Personne qui gère la plateforme ou une coopérative
"""

class Administrateur(models.Model):
    # L'administrateur est aussi un utilisateur
    utilisateur = models.OneToOneField(
        Utilisateur,
        primary_key=True,
        on_delete=models.CASCADE
    )
    # Coopérative gérée par l'administrateur
    cooperative = models.ForeignKey(
        'productions.Cooperative',
        on_delete=models.CASCADE
    )
    #Fonction occupée
    fonction = models.CharField(max_length=80)
    # Niveau de permission de l'administrateur
    NIVEAU_ACCES = [
        ('LECTURE', 'Lecture seule'),
        ('GESTION', 'Gestion'),
        ('TOTAL', 'Accès total'),
    ]
    niveau_acces = models.CharField(
        max_length=20,
        choices=NIVEAU_ACCES,
        default='GESTION'
    )

    # --- Droits dérivés du niveau d'accès ---
    @property
    def peut_consulter(self):
        """Tous les niveaux peuvent consulter les données."""
        return True

    @property
    def peut_gerer(self):
        """Gérer les membres / valider les productions."""
        return self.niveau_acces in ('GESTION', 'TOTAL')

    @property
    def peut_tout(self):
        """Accès complet (paramétrage, suppression…)."""
        return self.niveau_acces == 'TOTAL'

    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"

    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom} — {self.fonction}"
"""
TABLE : ACHETEUR
Client qui achète les produits agricoles
"""
class Acheteur(models.Model):
    # L'acheteur est lié à un compte utilisateur
    utilisateur = models.OneToOneField(
        Utilisateur,
        primary_key=True,
        on_delete=models.CASCADE
    )
    # Adresse où les commandes seront livrées
    adresse_livraison = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Acheteur"
        verbose_name_plural = "Acheteurs"

    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom}"

"""
TABLE : FORMATEUR
Personne qui crée les formations agricoles
"""
class Formateur(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        primary_key=True,
        on_delete=models.CASCADE
    )
    # Domaine de compétence
    specialite = models.CharField(max_length=100)
    # Présentation du formateur
    biographie = models.TextField()

    class Meta:
        verbose_name = "Formateur"
        verbose_name_plural = "Formateurs"

    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom}"
"""
TABLE : LIVREUR
Personne responsable du transport des commandes
"""
class Livreur(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        primary_key=True,
        on_delete=models.CASCADE
    )
    # Moyen de transport utilisé
    vehicule = models.CharField(max_length=50)
    # Zone où il peut effectuer les livraisons
    zone_couverture = models.CharField(max_length=100)
    # Disponible pour une nouvelle livraison ?
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Livreur"
        verbose_name_plural = "Livreurs"

    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom}"
