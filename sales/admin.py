from django.contrib import admin



from .models import (
    Commande,
    LigneCommande,
    Paiement,
    Livraison,
    Recu
)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Paiement)
admin.site.register(Livraison)
admin.site.register(Recu)