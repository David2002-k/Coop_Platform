from django.contrib import admin

from .models import Formation, SuiviFormation, Quiz


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 1


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_contenu', 'formateur', 'duree_estimee', 'statut')
    list_filter = ('type_contenu', 'statut')
    search_fields = ('titre',)
    list_per_page = 25
    autocomplete_fields = ('formateur',)
    inlines = [QuizInline]
    fieldsets = (
        ("Formation", {'fields': ('formateur', 'titre', 'description')}),
        ("Contenu", {'fields': ('type_contenu', 'contenu', 'fichier', 'duree_estimee', 'statut')}),
    )


@admin.register(SuiviFormation)
class SuiviFormationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'formation', 'progression', 'score_quiz', 'statut')
    list_filter = ('statut',)
    list_per_page = 25
    autocomplete_fields = ('membre', 'formation')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'formation', 'bonne_reponse')
    search_fields = ('question',)
    list_per_page = 25
    autocomplete_fields = ('formation',)
