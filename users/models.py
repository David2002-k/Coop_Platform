from django.db import models

"""
 TABLE : UTILISATEUR
 Cette table contient les informations communes
 à tous les acteurs de la plateforme :
 - Administrateur
 - Agriculteur/Membre
 - Acheteur
 - Formateur
 - Livreur
"""
class Utilisateur(models.Model):

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

    """ Email utilisé pour la connexion
     unique=True signifie qu'un email ne peut appartenir
    qu'à un seul utilisateur """
    email = models.EmailField(unique=True)

    # Mot de passe de l'utilisateur
    # Dans une vraie application il sera hashé
    mot_passe = models.CharField(max_length=255)

    # Numéro de téléphone
    telephone = models.CharField(max_length=50)

    # Adresse de l'utilisateur
    adresse = models.CharField(max_length=255)

    # Permet d'identifier le type d'utilisateur
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    # Permet de désactiver un compte sans le supprimer
    actif = models.BooleanField(default=True)

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

    # Niveau de permission
    niveau_acces = models.CharField(max_length=20)

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
