from django.db import models



"""
TABLE : FORMATION
Contient les cours proposés aux agriculteurs
Exemple : Techniques modernes de culture du maïs
"""
class Formation(models.Model):
    # Formateur responsable
    formateur = models.ForeignKey(
        'users.Formateur',
        on_delete=models.CASCADE
    )
    # Titre de la formation
    titre = models.CharField(max_length=200)
    # La description de la formation
    description = models.TextField()
    # Type de formation
    TYPE_CONTENU = [
        ('VIDEO', 'Vidéo'),
        ('COURS', 'Cours'),
        ('PDF', 'PDF'),
        ('QUIZ', 'Quiz'),
    ]
    type_contenu = models.CharField(
        max_length=20,
        choices=TYPE_CONTENU,
        default='COURS'
    )
     # Lien ou texte de la formation
    # Exemple : URL Youtube, texte du cours
    contenu = models.TextField(
        null=True,
        blank=True
    )
    # Fichier téléchargeable (PDF, vidéo…)
    fichier = models.FileField(
        upload_to='formations/',
        null=True,
        blank=True
    )
    # La durée estimée de la formation
    duree_estimee= models.CharField( max_length=50)
    # Etat de la formation
    # active / terminée
    statut = models.CharField(
        max_length=50,
        default="active"
    )
    def __str__(self):
        return self.titre




"""
TABLE : SUIVI_FORMATION
Historique des formations suivies
Permet de savoir quel agriculteur a suivi quelle formation
"""
class SuiviFormation(models.Model):
    # Agriculteur
    membre = models.ForeignKey(
        'users.Membre',
        on_delete=models.CASCADE
    )
    # Formation suivie
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE
    )
    # Progression
    # Exemple : 0, 50, 100 %
    progression = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    # Score obtenu au quiz
    # Exemple : 85/100
    score_quiz = models.IntegerField(default=0)
    # Etat de la formation : EN_COURS, TERMINEE, ABANDONNEE
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ABANDONNEE', 'Abandonnée'),
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_COURS'
    )
    def __str__(self):
        return f"{self.membre} - {self.formation}"
# TABLE : Quiz
class Quiz(models.Model):
    # Formation concernée
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    # Question du quiz
    question = models.TextField()
    # Les choix de réponses
    choix_a = models.CharField(max_length=255)
    choix_b = models.CharField(max_length=255)
    choix_c = models.CharField(max_length=255)
    # Exemple : A, B ou C
    bonne_reponse = models.CharField( max_length=1)
    def __str__(self):
        return self.question