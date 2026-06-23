from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from users.models import Utilisateur, Acheteur
from productions.models import Cooperative, Production, Produit


class AuthFlowTests(APITestCase):
    """Tests du parcours d'authentification et des permissions par rôle."""

    def setUp(self):
        self.coop = Cooperative.objects.create(
            nom="Coop Test", localisation="Ouaga")

    def _login(self, email, mot_passe):
        r = self.client.post('/api/token/',
                             {'email': email, 'password': mot_passe},
                             format='json')
        self.assertEqual(r.status_code, 200, r.content)
        return r.data['access']

    def test_inscription_puis_connexion(self):
        r = self.client.post('/api/register/', {
            'nom': 'Test', 'prenom': 'User', 'email': 'u@test.bf',
            'mot_passe': 'secret123', 'role': 'ACHETEUR',
            'adresse_livraison': 'Ouaga',
        }, format='json')
        self.assertEqual(r.status_code, 201, r.content)
        self.assertTrue(Acheteur.objects.filter(
            utilisateur__email='u@test.bf').exists())
        token = self._login('u@test.bf', 'secret123')
        self.assertTrue(token)

    def test_inscription_membre_exige_cooperative(self):
        r = self.client.post('/api/register/', {
            'nom': 'A', 'prenom': 'B', 'email': 'm@test.bf',
            'mot_passe': 'secret123', 'role': 'MEMBRE',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_me_renvoie_le_role(self):
        Utilisateur.objects.create_user(
            email='x@test.bf', mot_passe='secret123',
            nom='X', prenom='Y', role='FORMATEUR')
        token = self._login('x@test.bf', 'secret123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        r = self.client.get('/api/me/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['role'], 'FORMATEUR')

    def test_produits_lecture_publique(self):
        r = self.client.get('/api/produits/')
        self.assertEqual(r.status_code, 200)

    def test_acces_protege_sans_jeton(self):
        r = self.client.get('/api/commandes/')
        self.assertEqual(r.status_code, 401)
