from django.contrib import admin

from .models import Commande, LigneCommande, Paiement, Livraison, Recu


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    autocomplete_fields = ('produit',)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('reference', 'acheteur', 'montant_total', 'statut', 'date_commande')
    list_filter = ('statut',)
    search_fields = ('reference',)
    date_hierarchy = 'date_commande'
    list_per_page = 25
    autocomplete_fields = ('acheteur',)
    inlines = [LigneCommandeInline]
    fieldsets = (
        ("Commande", {'fields': ('acheteur', 'reference')}),
        ("Montant & statut", {'fields': ('montant_total', 'statut')}),
    )


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'montant', 'methode', 'statut', 'date_paiement')
    list_filter = ('statut', 'methode')
    search_fields = ('reference_transaction',)
    list_per_page = 25
    autocomplete_fields = ('commande',)


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'livreur', 'statut', 'date_livraison')
    list_filter = ('statut',)
    list_per_page = 25
    autocomplete_fields = ('commande', 'livreur')


@admin.register(Recu)
class RecuAdmin(admin.ModelAdmin):
    list_display = ('numero', 'paiement', 'montant', 'date_creation')
    search_fields = ('numero',)
    list_per_page = 25


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire', 'sous_total')
    autocomplete_fields = ('commande', 'produit')
    search_fields = ('produit__nom',)
