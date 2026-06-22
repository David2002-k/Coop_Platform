from django.contrib import admin



from .models import (
    Commande,
    LigneCommande,
    Paiement,
    Livraison
)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Paiement)
admin.site.register(Livraison)