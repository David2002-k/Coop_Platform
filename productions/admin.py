from django.contrib import admin

from .models import Cooperative, Production, Produit


@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'localisation', 'statut', 'date_creation')
    list_filter = ('statut',)
    search_fields = ('nom', 'localisation')
    list_per_page = 25
    fieldsets = (
        ("Informations", {'fields': ('nom', 'description', 'localisation')}),
        ("Suivi", {'fields': ('createur', 'statut')}),
    )
    autocomplete_fields = ('createur',)


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_culture', 'quantite', 'unite',
                    'membre', 'statut_validation', 'date_recolte')
    list_filter = ('statut_validation', 'type_culture')
    search_fields = ('nom', 'type_culture')
    list_editable = ('statut_validation',)
    date_hierarchy = 'date_recolte'
    ordering = ('-id',)
    list_per_page = 25
    autocomplete_fields = ('membre',)
    fieldsets = (
        ("Récolte", {'fields': ('membre', 'nom', 'type_culture')}),
        ("Quantité & date", {'fields': ('quantite', 'unite', 'date_recolte')}),
        ("Validation", {'fields': ('statut_validation',)}),
    )


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix_unitaire', 'quantite_stock', 'diponible')
    list_filter = ('diponible',)
    search_fields = ('nom',)
    list_editable = ('prix_unitaire', 'quantite_stock', 'diponible')
    list_per_page = 25
    autocomplete_fields = ('production',)
    fieldsets = (
        ("Produit", {'fields': ('production', 'nom', 'description', 'image')}),
        ("Vente", {'fields': ('prix_unitaire', 'quantite_stock', 'diponible')}),
    )
