from django.contrib import admin
from .models import Course, CourseGroups


# Register your models here.


class GroupsAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses',)

    class Meta:
        model = CourseGroups


admin.site.register(CourseGroups, GroupsAdmin)
admin.site.register(Course)
