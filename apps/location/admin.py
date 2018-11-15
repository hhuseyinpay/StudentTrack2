from django.contrib import admin

# Register your models here.

from location.models import Region, Area, ClassRoom


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


admin.site.register(Region, RegionAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
