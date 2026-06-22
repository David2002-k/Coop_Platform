from django.contrib import admin

from .models import (
    Utilisateur,
    Membre,
    Administrateur,
    Acheteur,
    Formateur,
    Livreur
)
admin.site.register(Utilisateur)
admin.site.register(Membre)
admin.site.register(Administrateur)
admin.site.register(Acheteur)
admin.site.register(Formateur)
admin.site.register(Livreur)