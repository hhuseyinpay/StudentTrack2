from django.contrib import admin

from .models import DailyStudy, Study

# class GroupsAdmin(admin.ModelAdmin):
#    filter_horizontal = ('courses',)

#    class Meta:
#        model = Group


# admin.site.unregister(Group)
# admin.site.register(Group, GroupsAdmin)

# Register your models here.
# class CeteleAdmin(admin.ModelAdmin):
#   fields = ('date',)

admin.site.register(Study)
admin.site.register(DailyStudy)

