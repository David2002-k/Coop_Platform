from rest_framework.permissions import BasePermission

"""
Permissions personnalisées basées sur le rôle de l'utilisateur.

Depuis que « Utilisateur » est le modèle d'authentification, request.user
porte directement le champ « role » et ses profils spécialisés
(membre, formateur, acheteur, livreur). Un administrateur (is_staff)
a accès à tout.
"""


class IsAdmin(BasePermission):
    # Administrateur
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == 'ADMIN')
        )


class IsAuthenticatedUser(BasePermission):
    # Utilisateur connecté
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAgriculteur(BasePermission):
    # Agriculteur = Membre
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_staff or hasattr(user, 'membre')


class IsFormateur(BasePermission):
    # Formateur
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_staff or hasattr(user, 'formateur')


class IsAcheteur(BasePermission):
    # Acheteur
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_staff or hasattr(user, 'acheteur')


class IsLivreur(BasePermission):
    # Livreur
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_staff or hasattr(user, 'livreur')
