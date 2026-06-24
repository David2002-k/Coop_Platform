# -*- coding: utf-8 -*-
"""Génère le PDF du cours « Comment acheter sur la plateforme »."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                ListFlowable, ListItem)
import os

VERT = HexColor("#2E7D32")
sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "Cours_Comment_Acheter.pdf")

styles = getSampleStyleSheet()
h1 = ParagraphStyle('h1', parent=styles['Heading1'], textColor=VERT, spaceAfter=10)
h2 = ParagraphStyle('h2', parent=styles['Heading2'], textColor=VERT, spaceBefore=12)
normal = ParagraphStyle('n', parent=styles['Normal'], fontSize=11, leading=16,
                        alignment=4, spaceAfter=6)

doc = SimpleDocTemplate(sortie, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                        leftMargin=2*cm, rightMargin=2*cm)
E = []

def p(txt): E.append(Paragraph(txt, normal))
def titre(txt): E.append(Paragraph(txt, h1))
def sous(txt): E.append(Paragraph(txt, h2))
def espace(h=8): E.append(Spacer(1, h))

titre("Comment acheter sur la plateforme des Coopératives Agricoles")
p("Ce cours explique, étape par étape, comment acheter des produits agricoles "
  "en ligne sur la plateforme, depuis la création de votre compte jusqu'à la "
  "réception de votre reçu. Il s'adresse à toute personne souhaitant commander "
  "des produits frais auprès des coopératives.")
espace()

sous("1. Créer votre compte acheteur")
p("Avant d'acheter, vous devez disposer d'un compte. Sur la page d'accueil, "
  "cliquez sur « Inscription », puis renseignez votre nom, votre prénom, votre "
  "adresse email, un mot de passe et votre adresse de livraison. Validez : votre "
  "compte est créé et vous êtes automatiquement connecté.")

sous("2. Se connecter")
p("Si vous avez déjà un compte, cliquez sur « Connexion », saisissez votre email "
  "et votre mot de passe. Une fois connecté, votre nom apparaît en haut de la page "
  "et le menu s'adapte à votre profil d'acheteur.")

sous("3. Parcourir le catalogue")
p("Cliquez sur « Catalogue » dans le menu. Vous y trouvez l'ensemble des produits "
  "disponibles, avec leur prix en francs CFA et la quantité encore en stock. Prenez "
  "le temps de comparer les produits proposés par les différentes coopératives.")

sous("4. Ajouter des produits au panier")
p("Sous chaque produit qui vous intéresse, cliquez sur « Ajouter au panier ». Vous "
  "pouvez ajouter plusieurs produits et revenir au catalogue autant de fois que "
  "nécessaire. Un message confirme chaque ajout.")

sous("5. Vérifier votre panier")
p("Cliquez sur « Panier » pour voir le récapitulatif : la liste des produits, les "
  "quantités, le prix unitaire et le total à payer. Vous pouvez retirer un article "
  "si vous changez d'avis.")

sous("6. Payer par Mobile Money")
p("Lorsque votre panier vous convient, saisissez votre numéro Mobile Money (Orange "
  "Money, Moov Money ou Wave) puis cliquez sur « Payer ». Vous êtes redirigé vers la "
  "page de paiement sécurisée. Suivez les instructions reçues sur votre téléphone pour "
  "valider la transaction.")

sous("7. Recevoir la confirmation et le reçu")
p("Dès que le paiement est confirmé, une page « Commande confirmée » s'affiche avec "
  "la référence de votre commande et le montant payé. Un reçu numérique est généré "
  "automatiquement : vous pouvez le retrouver à tout moment dans « Mes commandes ».")

sous("8. Suivre votre commande")
p("Dans « Mes commandes », vous suivez l'état de chacune de vos commandes (en "
  "attente, payée, livrée). La livraison est ensuite prise en charge par un livreur "
  "de la coopérative, qui met à jour le statut jusqu'à la réception.")

espace()
sous("En résumé")
E.append(ListFlowable([
    ListItem(Paragraph("Inscrivez-vous, puis connectez-vous.", normal)),
    ListItem(Paragraph("Parcourez le catalogue et ajoutez au panier.", normal)),
    ListItem(Paragraph("Vérifiez le panier, payez par Mobile Money.", normal)),
    ListItem(Paragraph("Recevez votre reçu et suivez la livraison.", normal)),
], bulletType='1'))

espace()
p("<i>Conseil : gardez votre mot de passe confidentiel et vérifiez toujours le "
  "montant affiché avant de confirmer le paiement.</i>")

doc.build(E)
print("PDF généré :", sortie)
