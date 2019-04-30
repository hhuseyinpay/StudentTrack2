from rest_framework.permissions import BasePermission


class CanEditClassroom(BasePermission):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff.is_executive() and obj.area.executives.filter(id=staff.id).exists():
            return True
        if staff.is_admin() and obj.area.region.admins.filter(id=staff.id).exists():
            return True
        return False


class CanEditArea(BasePermission):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff.is_executive() and obj.executives.filter(id=staff.id).exists():
            return True
        if staff.is_admin() and obj.region.admins.filter(id=staff.id).exists():
            return True
        return False
