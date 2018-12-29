from django.contrib import admin

from .models import UserSyllabus, Content, Syllabus

admin.site.register(Content)
admin.site.register(UserSyllabus)


@admin.register(Syllabus)
class MahalleAdmin(admin.ModelAdmin):
    filter_horizontal = ('contents',)
