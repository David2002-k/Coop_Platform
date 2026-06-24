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

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Identité', {'fields': ('nom', 'prenom', 'telephone', 'adresse')}),
        ('Rôle & statut', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
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
    search_fields = ('numero_adhesion',)


@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cooperative', 'fonction', 'niveau_acces')
    list_filter = ('niveau_acces',)


@admin.register(Acheteur)
class AcheteurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'adresse_livraison')


@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'specialite')


@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'vehicule', 'zone_couverture', 'disponible')
    list_filter = ('disponible',)

admin.site.site_header = "Administration — Coopératives Agricoles"
admin.site.site_title = "Coopératives Agricoles"
admin.site.index_title = "Gestion de la plateforme"
