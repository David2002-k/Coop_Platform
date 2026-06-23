from django.utils import timezone
from rest_framework import serializers

from .models import (
    Utilisateur,
    Membre,
    Administrateur,
    Acheteur,
    Formateur,
    Livreur,
)


class UtilisateurSerializer(serializers.ModelSerializer):
    """Représentation publique d'un utilisateur (sans le mot de passe)."""

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'nom', 'prenom', 'email',
            'telephone', 'adresse', 'role',
            'is_active', 'is_staff', 'date_inscription',
        ]
        read_only_fields = ['id', 'is_staff', 'date_inscription']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Inscription d'un nouvel utilisateur.

    Crée le compte de connexion (table utilisateur) ET, selon le rôle
    choisi, le profil spécialisé correspondant (membre, acheteur,
    formateur, livreur ou administrateur).

    Les champs spécifiques au rôle sont optionnels et passés à plat :
      - MEMBRE / ADMIN : cooperative (id) requis
      - MEMBRE     : numero_adhesion, montant_cotisation
      - ADMIN      : fonction, niveau_acces
      - ACHETEUR   : adresse_livraison
      - FORMATEUR  : specialite, biographie
      - LIVREUR    : vehicule, zone_couverture
    """

    mot_passe = serializers.CharField(write_only=True, min_length=4)

    # Champs de profil optionnels (non stockés sur Utilisateur)
    cooperative = serializers.IntegerField(required=False, write_only=True)
    numero_adhesion = serializers.CharField(required=False, write_only=True)
    montant_cotisation = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, write_only=True)
    fonction = serializers.CharField(required=False, write_only=True)
    niveau_acces = serializers.CharField(required=False, write_only=True)
    adresse_livraison = serializers.CharField(required=False, write_only=True)
    specialite = serializers.CharField(required=False, write_only=True)
    biographie = serializers.CharField(required=False, write_only=True)
    vehicule = serializers.CharField(required=False, write_only=True)
    zone_couverture = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'nom', 'prenom', 'email', 'mot_passe',
            'telephone', 'adresse', 'role',
            # champs de profil
            'cooperative', 'numero_adhesion', 'montant_cotisation',
            'fonction', 'niveau_acces', 'adresse_livraison',
            'specialite', 'biographie', 'vehicule', 'zone_couverture',
        ]

    def validate(self, data):
        role = data.get('role', 'MEMBRE')
        if role in ('MEMBRE', 'ADMIN') and not data.get('cooperative'):
            raise serializers.ValidationError(
                {"cooperative": "Une coopérative est requise pour ce rôle."}
            )
        return data

    def create(self, validated_data):
        # On isole les champs de profil
        profil_keys = [
            'cooperative', 'numero_adhesion', 'montant_cotisation',
            'fonction', 'niveau_acces', 'adresse_livraison',
            'specialite', 'biographie', 'vehicule', 'zone_couverture',
        ]
        profil = {k: validated_data.pop(k) for k in profil_keys
                  if k in validated_data}

        mot_passe = validated_data.pop('mot_passe')
        role = validated_data.get('role', 'MEMBRE')

        utilisateur = Utilisateur.objects.create_user(
            mot_passe=mot_passe, **validated_data
        )

        # Création du profil spécialisé selon le rôle
        from productions.models import Cooperative
        coop = None
        if profil.get('cooperative'):
            coop = Cooperative.objects.filter(pk=profil['cooperative']).first()
            if coop is None:
                utilisateur.delete()
                raise serializers.ValidationError(
                    {"cooperative": "Coopérative introuvable."}
                )

        if role == 'MEMBRE':
            Membre.objects.create(
                utilisateur=utilisateur,
                cooperative=coop,
                numero_adhesion=profil.get('numero_adhesion', ''),
                date_adhesion=timezone.now().date(),
                montant_cotisation=profil.get('montant_cotisation', 0),
            )
        elif role == 'ADMIN':
            utilisateur.is_staff = True
            utilisateur.save(update_fields=['is_staff'])
            Administrateur.objects.create(
                utilisateur=utilisateur,
                cooperative=coop,
                fonction=profil.get('fonction', ''),
                niveau_acces=profil.get('niveau_acces', 'standard'),
            )
        elif role == 'ACHETEUR':
            Acheteur.objects.create(
                utilisateur=utilisateur,
                adresse_livraison=profil.get('adresse_livraison', ''),
            )
        elif role == 'FORMATEUR':
            Formateur.objects.create(
                utilisateur=utilisateur,
                specialite=profil.get('specialite', ''),
                biographie=profil.get('biographie', ''),
            )
        elif role == 'LIVREUR':
            Livreur.objects.create(
                utilisateur=utilisateur,
                vehicule=profil.get('vehicule', ''),
                zone_couverture=profil.get('zone_couverture', ''),
            )

        return utilisateur

    def to_representation(self, instance):
        return UtilisateurSerializer(instance).data
