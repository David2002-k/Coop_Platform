from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import (
    Utilisateur,
    Membre,
    Administrateur,
    Acheteur,
    Formateur,
    Livreur,
)


class UtilisateurCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ('email', 'nom', 'prenom', 'role')


class UtilisateurChangeForm(UserChangeForm):
    class Meta:
        model = Utilisateur
        fields = '__all__'


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    add_form = UtilisateurCreationForm
    form = UtilisateurChangeForm
    model = Utilisateur

    list_display = ('email', 'nom', 'prenom', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('email',)
    list_per_page = 25
    list_display_links = ('email',)
    # Listes à double colonne avec recherche (bien plus pratiques)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        ("Connexion", {'fields': ('email', 'password')}),
        ('Identité', {'fields': ('nom', 'prenom', 'telephone', 'adresse')}),
        ('Rôle & statut', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions avancées', {
            'classes': ('collapse',),  # repliée par défaut : moins de complexité
            'description': "Réservé aux cas avancés. Le rôle et « statut équipe » "
                           "suffisent dans la plupart des cas.",
            'fields': ('groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'role',
                       'password1', 'password2'),
        }),
    )


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cooperative', 'numero_adhesion', 'statut_cotisation')
    list_filter = ('statut_cotisation', 'cooperative')
    search_fields = ('numero_adhesion', 'utilisateur__email',
                     'utilisateur__nom', 'utilisateur__prenom')
    list_per_page = 25
    autocomplete_fields = ('utilisateur', 'cooperative')


@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cooperative', 'fonction', 'niveau_acces')
    list_filter = ('niveau_acces',)
    search_fields = ('utilisateur__email', 'utilisateur__nom')
    list_per_page = 25
    autocomplete_fields = ('utilisateur', 'cooperative')


@admin.register(Acheteur)
class AcheteurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'adresse_livraison')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'utilisateur__prenom')
    list_per_page = 25
    autocomplete_fields = ('utilisateur',)


@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'specialite')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'specialite')
    list_per_page = 25
    autocomplete_fields = ('utilisateur',)


@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'vehicule', 'zone_couverture', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'zone_couverture')
    list_per_page = 25
    autocomplete_fields = ('utilisateur',)

# On retire la page « Groupes » de Django : l'application gère les accès
# via le champ Rôle et le niveau d'accès administrateur, pas via les
# groupes/permissions techniques (qui n'ont aucun effet ici).
from django.contrib.auth.models import Group
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

admin.site.site_header = "Administration — Coopératives Agricoles"
admin.site.site_title = "Coopératives Agricoles"
admin.site.index_title = "Gestion de la plateforme"
