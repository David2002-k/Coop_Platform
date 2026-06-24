"""
Intégration de la passerelle de paiement MoneyFusion (FusionPay).

Flux :
  1. initier_paiement() envoie la commande à l'URL d'API personnelle
     du marchand (configurée dans .env : MONEYFUSION_API_URL) et reçoit
     une URL de paiement + un token.
  2. Le client est redirigé vers cette URL (paiement Mobile Money).
  3. Après paiement, MoneyFusion appelle return_url / webhook_url ;
     verifier_paiement(token) confirme le statut réel.

Documentation : https://docs.moneyfusion.net
"""
import requests
from django.conf import settings

# URL d'API personnelle du marchand (depuis le tableau de bord MoneyFusion).
# Exemple : https://www.pay.moneyfusion.net/<votre_identifiant>/
API_URL = getattr(settings, 'MONEYFUSION_API_URL', '')

# URL officielle de vérification d'un paiement par son token.
NOTIF_URL = "https://www.pay.moneyfusion.net/paiementNotif/"

TIMEOUT = 30


def est_configure():
    """True si une URL d'API MoneyFusion est renseignée."""
    return bool(API_URL)


def initier_paiement(total, nom_client, numero, articles,
                     return_url, webhook_url, infos=None):
    """
    Crée une demande de paiement chez MoneyFusion.

    - total      : montant total (nombre)
    - nom_client : nom du client
    - numero     : numéro Mobile Money de l'acheteur
    - articles   : liste de dicts {libellé: prix}
    - return_url : page de retour (HTTPS publique)
    - webhook_url: endpoint de notification (HTTPS publique)
    - infos      : liste de données libres renvoyées au webhook

    Retourne le dict JSON de MoneyFusion : {statut, token, message, url}.
    Lève une exception en cas d'échec réseau.
    """
    payload = {
        "totalPrice": float(total),
        "article": articles,
        "personal_Info": infos or [],
        "numeroSend": numero,
        "nomclient": nom_client,
        "return_url": return_url,
        "webhook_url": webhook_url,
    }
    reponse = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    reponse.raise_for_status()
    return reponse.json()


def verifier_paiement(token):
    """
    Vérifie le statut réel d'un paiement auprès de MoneyFusion.

    Retourne le dict JSON. Le statut se trouve typiquement dans
    data['statut'] avec les valeurs : 'paid', 'pending', 'no paid',
    'failure'.
    """
    reponse = requests.get(NOTIF_URL + str(token), timeout=TIMEOUT)
    reponse.raise_for_status()
    return reponse.json()


def est_paye(resultat_verification):
    """Interprète la réponse de verifier_paiement() : True si payé."""
    data = resultat_verification.get('data', resultat_verification)
    statut = str(data.get('statut', '')).lower()
    return statut in ('paid', 'payé', 'paye', 'success', 'successful')
