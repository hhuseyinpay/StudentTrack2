from rest_framework import permissions


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


class IsAdminExecutive(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.is_executive or request.user.profile.is_admin:
            return True
        return False


class IsTeExAd(permissions.BasePermission):
    def has_permission(self, request, view):
        p = request.user.profile
        if p.is_teacher or p.is_executive or p.is_admin:
            return True
        return False


def is_authority(authority_user, low_authority_profile):
    if authority_user == low_authority_profile.user:
        return True

    if low_authority_profile.classroom \
            and low_authority_profile.is_student \
            and authority_user.profile.is_teacher \
            and authority_user in low_authority_profile.classroom.teachers.all():
        return True

    if low_authority_profile.related_area \
            and not low_authority_profile.is_executive \
            and not low_authority_profile.is_admin \
            and authority_user.profile.is_executive \
            and authority_user in low_authority_profile.related_area.executives.all():
        return True

    if low_authority_profile.related_region \
            and not low_authority_profile.is_admin \
            and authority_user.profile.is_admin \
            and authority_user in low_authority_profile.related_region.admin.all():
        return True
    return False


class CanEditProfile(IsTeExAd):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return is_authority(user, obj)
