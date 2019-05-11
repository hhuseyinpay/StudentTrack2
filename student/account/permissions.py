from rest_framework.permissions import BasePermission

from student.location.models import ClassRoom, Area, Region


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_teacher():
            return True
        return False


class IsExecutive(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_executive():
            return True
        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_admin():
            return True
        return False


class IsExecutiveAdmin(BasePermission):
    def has_permission(self, request, view):
        staff = request.user
        if staff and (staff.is_executive() or staff.is_admin()):
            return True
        return False


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        staff = request.user
        if staff and (staff.is_teacher() or staff.is_executive() or staff.is_admin()):
            return True
        return False


def is_authority(authority_user, low_authority_user):
    if authority_user == low_authority_user:
        return True
    if authority_user.is_teacher() and \
            low_authority_user.classroom in ClassRoom.objects.filter(teachers=authority_user):
        return True
    if authority_user.is_executive() and \
            low_authority_user.classroom.area in Area.objects.filter(executives=authority_user):
        return True
    if authority_user.is_admin() and \
            low_authority_user.classroom.area.region in Region.objects.filter(admins=authority_user):
        return True
    return False


class CanEditClassroom(IsExecutiveAdmin):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff.is_executive() and staff in obj.area.executives.all():
            return True
        if staff.is_admin() and staff in obj.area.region.admins.all():
            return True
        return False


class CanEditUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff == obj:
            return True

        # user yeni oluşturuluyorsa
        if obj.is_new():
            return True

        if obj.is_student():
            if staff.is_teacher() and ClassRoom.objects.filter(students=obj, teachers=staff).exists():
                return True
            elif staff.is_executive() and ClassRoom.objects.filter(students=obj, area__executives=staff).exists():
                return True
            elif staff.is_admin() and ClassRoom.objects.filter(students=obj, area__region__admins=staff).exists():
                return True
        elif obj.is_teacher():
            if staff.is_executive() and ClassRoom.objects.filter(teachers=obj, area__executives=staff).exists():
                return True
            elif staff.is_admin() and ClassRoom.objects.filter(teachers=obj, area__region__admins=staff).exists():
                return True
        elif obj.is_executive():
            if staff.is_admin() and Area.objects.filter(executives=obj, region__admins=staff).exists():
                return True

        return False


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


