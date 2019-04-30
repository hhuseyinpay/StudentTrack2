from rest_framework.permissions import BasePermission

from student.account.permissions import IsStaff, is_authority, CanEditUser


class CanEditSyllabus2(IsStaff):
    def has_object_permission(self, request, view, obj):
        current_user = request.user
        usersyllabus_profile = obj.user.profile
        return is_authority(current_user, usersyllabus_profile)


class IsSyllabusOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanEditSyllabus(IsStaff):
    def has_object_permission(self, request, view, obj):
        return CanEditUser().has_object_permission(request, view, obj.user)
