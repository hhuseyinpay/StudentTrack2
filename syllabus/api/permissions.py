from rest_framework import permissions

from accounts.api.permissions import IsTeExAd, is_authority


class CanEditSyllabus(IsTeExAd):
    def has_object_permission(self, request, view, obj):
        current_user = request.user
        usersyllabus_profile = obj.user.profile
        return is_authority(current_user, usersyllabus_profile)
