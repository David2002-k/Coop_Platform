from django.contrib import admin

from .models import Formation, SuiviFormation, Quiz


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_contenu', 'formateur', 'duree_estimee', 'statut')
    list_filter = ('type_contenu', 'statut')
    search_fields = ('titre',)
    inlines = [QuizInline]


@admin.register(SuiviFormation)
class SuiviFormationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'formation', 'progression', 'score_quiz', 'statut')
    list_filter = ('statut',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'formation', 'bonne_reponse')
    search_fields = ('question',)
