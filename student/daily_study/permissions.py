from rest_framework.permissions import BasePermission

from student.account.permissions import IsStaff, is_authority, CanEditUser


class CanEditDailyStudy_OLD(IsStaff):
    def has_object_permission(self, request, view, obj):
        current_user = request.user
        dailystudy_profile = obj.user.profile
        return is_authority(current_user, dailystudy_profile)


class IsDailyStudyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanEditDailyStudy(IsStaff):
    def has_object_permission(self, request, view, obj):
        return CanEditUser().has_object_permission(request, view, obj.user)
