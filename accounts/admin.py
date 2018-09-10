from django.contrib import admin

from .models import Profile, ClassRoom, Area, Region, Groups


# Register your models here.

class RegionAdmin(admin.ModelAdmin):
    filter_horizontal = ('admins',)

    class Meta:
        model = Region


class AreaAdmin(admin.ModelAdmin):
    filter_horizontal = ('executives',)

    class Meta:
        model = Area


class ClassRoomAdmin(admin.ModelAdmin):
    filter_horizontal = ('teachers',)

    class Meta:
        model = ClassRoom


class GroupsAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses',)

    class Meta:
        model = ClassRoom


admin.site.register(Region, RegionAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)

admin.site.register(Groups, GroupsAdmin)

admin.site.register(Profile)
