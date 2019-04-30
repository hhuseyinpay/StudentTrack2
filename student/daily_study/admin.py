from django.contrib import admin
from django.contrib.admin import DateFieldListFilter, BooleanFieldListFilter

from .models import DailyStudy, Study

# class GroupsAdmin(admin.ModelAdmin):
#    filter_horizontal = ('courses',)

#    class Meta:
#        model = Group


# admin.site.unregister(Group)
# admin.site.register(Group, GroupsAdmin)

# Register your models here.
# class StudentAdmin(admin.ModelAdmin):
#   fields = ('date',)

admin.site.register(Study)


# admin.site.register(DailyStudy)


class StudyAdmin(admin.StackedInline):
    model = Study


@admin.register(DailyStudy)
class DailyStudyAdmin(admin.ModelAdmin):
    inlines = [StudyAdmin]
    max_num = 10

