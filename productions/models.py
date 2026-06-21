from django.db import models


"""
 TABLE : COOPERATIVE
 Regroupe les agriculteurs autour d'une organisation
"""
class Cooperative(models.Model):

    # Nom de la coopérative
    nom = models.CharField(
        max_length=150
    )

    # Description de la coopérative
    description = models.TextField(
        null=True,
        blank=True
    )

    # Localisation géographique
    localisation = models.CharField(max_length=150)

    # Date de création
    date_creation = models.DateField(auto_now_add=True)

    # Etat de la coopérative
    # Exemple : active, suspendue
    statut = models.CharField(
        max_length=50,
        default="active"
    )
    def __str__(self):
        return self.nom

"""
 TABLE : PRODUCTION
 Représente ce que produit un agriculteur
 Exemple :Maïs : 500 kg, Tomate : 200 kg
"""

class Production(models.Model):
    # Agriculteur qui réalise la production
    # Relation avec la table Membre
    membre = models.ForeignKey(
        'users.Membre',
        on_delete=models.CASCADE
    )
    # Nom de la culture
    nom = models.CharField(
        max_length=100
    )
    #Le type de culture 
    type_culture = models.CharField(max_length=80)
    # Quantité produite
    quantite = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Unité :kg, tonne, sac
    unite = models.CharField(max_length=30)
    # Date de la recolte
    date_recolte = models.DateField()
    # Etat de la production
    statut_validation =models.BooleanField(default=False)
    def __str__(self):
        return self.nom




"""
 TABLE : PRODUIT
 Produit disponible à la vente
 Une production peut donner plusieurs produits
"""

class Produit(models.Model):
    # Production d'origine
    production = models.ForeignKey(
        Production,
        on_delete=models.CASCADE
    )

    # Nom du produit vendu
    nom = models.CharField(max_length=150)

    # Description commerciale
    description = models.TextField(
        null=True,
        blank=True
    )
    # Prix unitaire
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Quantité disponible
    quantite_stock = models.IntegerField()

    #diponibilité du produit
    diponible = models.BooleanField(default=True)

    # Image du produit
    # Pillow installé précédemment sera utilisé
    image = models.ImageField(
        upload_to="static/images/",
        null=True,
        blank=True
    )
    def __str__(self):
        return self.nom
