# 🌾 Plateforme de Gestion des Coopératives Agricoles

Application web (Django + Django REST Framework) destinée aux coopératives
agricoles du Burkina Faso. Elle centralise la **gestion des membres**, le
**suivi des productions**, la **vente en ligne** et la **formation** des
agriculteurs.

> Université Virtuelle du Burkina Faso · Licence 3 Mathématiques-Informatique · 2025–2026

---

## 1. Fonctionnalités

- **Utilisateurs & rôles** : un compte de connexion unique (`Utilisateur`)
  servant de modèle d'authentification, décliné en 5 profils :
  Administrateur, Membre (agriculteur), Acheteur, Formateur, Livreur.
- **Authentification JWT** : connexion par email + mot de passe.
- **Productions & catalogue** : récoltes → validation → produits vendables.
- **Ventes** : commandes, lignes de commande, paiements, **génération
  automatique du reçu** lorsqu'un paiement passe au statut « payé »,
  livraisons.
- **Formation** : contenus pédagogiques, quiz, suivi de progression.
- **API REST** sécurisée par des permissions basées sur le rôle.
- **Interface d'administration** Django complète.

## 2. Pile technique

Python 3 · Django 5 · Django REST Framework · SimpleJWT · Bootstrap 5 ·
PostgreSQL (cible) / SQLite (par défaut, sans configuration).

---

## 3. Installation et lancement (5 minutes)

```bash
# 1. Créer et activer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Base de données PostgreSQL (cible du projet)
#    a. Créer la base et l'utilisateur :
#       sudo -u postgres psql
#         CREATE USER coop_user WITH PASSWORD 'coop_pass';
#         CREATE DATABASE coop_platform OWNER coop_user;
#         ALTER USER coop_user CREATEDB;
#         \q
#    b. Copier la configuration : cp .env.example .env
#    (Sans .env, l'app utilise SQLite — pratique pour un essai rapide.)

# 4. Créer les tables
python manage.py migrate

# 5. (Optionnel mais recommandé) Charger des données de démonstration
python manage.py seed_demo

# 6. Démarrer le serveur
python manage.py runserver
```

Ouvrez ensuite **http://127.0.0.1:8000/**.

> **Base de données** : sans fichier `.env`, l'application utilise
> automatiquement **SQLite** — rien à installer. Pour PostgreSQL, copiez
> `.env.example` en `.env` et renseignez les variables `DB_*`.

### Créer un super-utilisateur (accès à l'admin)

```bash
python manage.py createsuperuser
```

(La commande `seed_demo` crée déjà un super-admin : `admin@coop.bf` /
mot de passe `demo1234`.)

---

## 4. Comptes de démonstration

Après `python manage.py seed_demo` (mot de passe commun : **`demo1234`**) :

| Email               | Rôle                      |
|---------------------|---------------------------|
| `admin@coop.bf`     | Super-administrateur      |
| `gestion@coop.bf`   | Administrateur coopérative|
| `membre@coop.bf`    | Membre (agriculteur)      |
| `acheteur@coop.bf`  | Acheteur                  |
| `formateur@coop.bf` | Formateur                 |
| `livreur@coop.bf`   | Livreur                   |

---

## 5. Points d'entrée de l'API

| Méthode | URL                       | Accès            |
|---------|---------------------------|------------------|
| POST    | `/api/register/`          | Public           |
| POST    | `/api/token/`             | Public (login)   |
| POST    | `/api/token/refresh/`     | Public           |
| GET     | `/api/me/`                | Authentifié      |
| GET/POST| `/api/cooperatives/`      | Membre / Admin   |
| GET/POST| `/api/productions/`       | Membre           |
| GET/POST| `/api/produits/`          | Lecture publique |
| GET/POST| `/api/commandes/`         | Acheteur         |
| GET/POST| `/api/paiements/`         | Acheteur         |
| GET     | `/api/recus/`             | Acheteur         |
| GET/POST| `/api/livraisons/`        | Livreur          |
| GET/POST| `/api/formations/`        | Formateur        |
| GET/POST| `/api/suiviformations/`   | Membre           |

---

## 6. Démarches pour tester

### a) Via le navigateur (le plus simple)

1. Lancez `python manage.py seed_demo` puis `python manage.py runserver`.
2. Page d'accueil : **http://127.0.0.1:8000/**
3. Administration : **http://127.0.0.1:8000/admin/**
   (connexion `admin@coop.bf` / `demo1234`).
4. API navigable : **http://127.0.0.1:8000/api/produits/**

### b) Via cURL (test du parcours complet)

```bash
# 1. Connexion → récupérer le jeton d'accès
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"membre@coop.bf","password":"demo1234"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access'])")

# 2. Profil de l'utilisateur connecté
curl http://127.0.0.1:8000/api/me/ -H "Authorization: Bearer $TOKEN"

# 3. Lister ses productions
curl http://127.0.0.1:8000/api/productions/ -H "Authorization: Bearer $TOKEN"

# 4. Inscription d'un nouvel acheteur (public)
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"nom":"Diallo","prenom":"Awa","email":"awa@coop.bf",
       "mot_passe":"secret123","role":"ACHETEUR",
       "adresse_livraison":"Bobo-Dioulasso"}'
```

### c) Vérification automatique

```bash
python manage.py check        # contrôle de configuration
python manage.py test users   # exécute la suite de tests (5 tests)
```

---

## 7. Structure du projet

```
core/         Configuration Django (settings, urls, permissions)
users/        Utilisateurs, rôles et inscription
productions/  Coopératives, productions, produits
sales/        Commandes, paiements, reçus, livraisons
formation/    Formations, quiz, suivi
templates/    Pages HTML (Bootstrap)
static/       CSS / JS
```
