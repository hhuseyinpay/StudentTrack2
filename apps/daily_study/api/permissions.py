from apps.accounts.api.permissions import IsTeacherExecutiveAdmin, is_authority


class CanEditDailyStudy(IsTeacherExecutiveAdmin):
    def has_object_permission(self, request, view, obj):
        current_user = request.user
        dailystudy_profile = obj.user.profile
        return is_authority(current_user, dailystudy_profile)
