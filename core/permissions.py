from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    # Administrateur
    def has_permission(self, request, view):
        return request.user.is_staff

class IsAuthenticatedUser(BasePermission):
    # Utilisateur connecté
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsAgriculteur(BasePermission):
    # Agriculteur = Membre
    def has_permission(self, request, view):
        return hasattr(request.user, 'membre')

class IsFormateur(BasePermission):
    # Formateur
    def has_permission(self, request, view):
        return hasattr(request.user, 'formateur')

class IsAcheteur(BasePermission):
    # Acheteur
    def has_permission(self, request, view):
        return hasattr(request.user, 'acheteur')

class IsLivreur(BasePermission):
    # Livreur
    def has_permission(self, request, view):
        return hasattr(request.user, 'livreur')