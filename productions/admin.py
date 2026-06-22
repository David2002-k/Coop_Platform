from django.contrib import admin


from .models import (
    Cooperative,
    Production,
    Produit
)
admin.site.register(Cooperative)
admin.site.register(Production)
admin.site.register(Produit)