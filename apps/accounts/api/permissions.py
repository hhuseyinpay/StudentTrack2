from rest_framework import permissions
from accounts.models import ClassRoom, Area, Region


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.is_teacher:
            return True
        return False


class IsExecutive(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.is_executive:
            return True
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.is_admin:
            return True
        return False


class IsExecutiveAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.is_executive or request.user.profile.is_admin:
            return True
        return False


class IsTeacherExecutiveAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        p = request.user.profile
        if p.is_teacher or p.is_executive or p.is_admin:
            return True
        return False


def is_authority(authority_user, low_authority_profile):
    authority_profile = authority_user.profile
    if authority_user == low_authority_profile.user:
        return True
    if authority_profile.is_teacher and \
            low_authority_profile.classroom in ClassRoom.objects.filter(teachers=authority_user):
        return True
    if authority_profile.is_executive and \
            low_authority_profile.classroom.area in Area.objects.filter(executives=authority_user):
        return True
    if authority_profile.is_admin and \
            low_authority_profile.classroom.area.region in Region.objects.filter(admins=authority_user):
        return True
    return False


class CanEditProfile(IsTeacherExecutiveAdmin):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff == obj.user:
            return True
        if staff.profile.is_teacher and obj.is_student:
            if obj.classroom in ClassRoom.objects.filter(teachers=staff):
                return True
        if staff.profile.is_executive and not obj.is_executive and not obj.is_admin:
            if obj.classroom.area in Area.objects.filter(executives=staff):
                return True
        elif staff.profile.is_admin and not obj.is_admin:
            if obj.classroom.area.region in Region.objects.filter(admins=staff):
                return True
        return False


class CanEditClassroom(IsExecutiveAdmin):
    def has_object_permission(self, request, view, obj):
        staff = request.user
        if staff.profile.is_executive and staff in obj.area.executives.all():
            return True
        if staff.profile.is_admin and staff in obj.area.region.admins.all():
            return True
        return False
