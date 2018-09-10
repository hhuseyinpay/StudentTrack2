from django.contrib import admin

from .models import UserSyllabus, Content, Syllabus

admin.site.register(Syllabus)
admin.site.register(Content)
admin.site.register(UserSyllabus)
