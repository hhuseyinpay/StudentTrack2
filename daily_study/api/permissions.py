from rest_framework import permissions

from accounts.api.permissions import IsTeExAd, is_authority


class CanEditDailyStudy(IsTeExAd):
    def has_object_permission(self, request, view, obj):
        current_user = request.user
        dailystudy_profile = obj.user.profile
        return is_authority(current_user, dailystudy_profile)
