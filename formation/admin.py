from django.contrib import admin

from .models import (
    Formation,
    SuiviFormation
)
admin.site.register(Formation)
admin.site.register(SuiviFormation)

from .models import Quiz
admin.site.register(Quiz)