from django.db import models
import uuid



"""
 TABLE : COMMANDE
 Représente une commande passée par un acheteur
 Exemple : Un acheteur commande 5 sacs de maïs
"""
class Commande(models.Model):
    # Acheteur qui passe la commande
    # Relation avec users.Acheteur
    acheteur = models.ForeignKey(
        'users.Acheteur',
        on_delete=models.CASCADE
    )
    reference = models.CharField(
        max_length= 30,
        unique=True
    )
    # Date de création automatique
    date_commande = models.DateTimeField(auto_now_add=True)
    # Montant total de la commande
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    # Etat de la commande
    # Exemple : en attente, validée, livrée, annulée
    statut = models.CharField(
        max_length=50,
        default="en attente"
    )
    def __str__(self):
        return f"Commande {self.id}"


"""
TABLE : LIGNE COMMANDE
Détaille les produits contenus dans une commande
Une commande peut contenir plusieurs produits
"""
class LigneCommande(models.Model):
    # Commande concernée
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE
    )
    # Produit acheté
    produit = models.ForeignKey(
        'productions.Produit',
        on_delete=models.CASCADE
    )
    # Quantité commandée
    quantite = models.IntegerField()
    # Prix au moment de l'achat
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Montant total de cette ligne
    sous_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    def save(self, *args, **kwargs):
        # Calcul automatique avant l'enregistrement
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.produit} - {self.quantite}"


"""
TABLE : PAIEMENT
Gère le paiement d'une commande
"""
class Paiement(models.Model):
    # Une commande possède un paiement
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE
    )
    # Montant payé
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Méthode de paiement
    # Exemple : Mobile Money, Carte bancaire, Espèces
    methode = models.CharField(max_length=50)
    # Statut du paiement : payé, en attente, refusé
    statut = models.CharField(
        max_length=50,
        default="en attente"
    )
    date_paiement = models.DateTimeField(auto_now_add=True )
    # Référence donnée par le service de paiement
    # Exemple : OM123456789
    reference_transaction = models.CharField(
        max_length=100,
        unique=True
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.statut == "payé":
            Recu.objects.get_or_create(
            paiement=self,
            defaults={
                "numero": "REC-" + str(uuid.uuid4())[:8],
                "montant": self.montant
            }
        )
    def __str__(self):
        return f"Paiement {self.id}"


"""
TABLE : LIVRAISON
Gestion de la livraison des commandes
"""
class Livraison(models.Model):
    # Commande à livrer
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE
    )
    # Livreur affecté
    livreur = models.ForeignKey(
        'users.Livreur',
        on_delete=models.CASCADE
    )
    adresse_livraison = models.CharField(max_length=255)
    date_livraison = models.DateTimeField(
        null=True,
        blank=True
    )
    statut = models.CharField(
        max_length=50,
        default="en préparation"
    )
    def __str__(self):
        return f"Livraison {self.id}"

#Table : Reçu
class Recu(models.Model):
    # Paiement concerné
    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE
    )
    # Numéro du reçu
    numero = models.CharField(
        max_length=50,
        unique=True
    )
    # Date de génération
    date_creation = models.DateTimeField(auto_now_add=True)
    # Montant payé
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    def __str__(self):
        return f"Reçu {self.numero}"
