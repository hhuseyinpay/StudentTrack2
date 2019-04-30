from django.contrib import admin

from .models import UserSyllabus, Content, Syllabus


class ContentAdmin(admin.StackedInline):
    model = Content


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    inlines = [ContentAdmin]


admin.site.register(Content)
admin.site.register(UserSyllabus)
