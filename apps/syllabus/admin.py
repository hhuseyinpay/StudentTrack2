from django.contrib import admin

from .models import UserSyllabus, Content, Syllabus


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    filter_horizontal = ('contents',)


admin.site.register(Content)
admin.site.register(UserSyllabus)
