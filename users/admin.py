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


admin.site.register(Membre)
admin.site.register(Administrateur)
admin.site.register(Acheteur)
admin.site.register(Formateur)
admin.site.register(Livreur)

admin.site.site_header = "Administration — Coopératives Agricoles"
admin.site.site_title = "Coopératives Agricoles"
admin.site.index_title = "Gestion de la plateforme"
