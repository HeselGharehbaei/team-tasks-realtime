from rest_framework import permissions
from .models import Team
from .models import Task

class IsTeamMember(permissions.BasePermission):
    """
    فقط اعضای تیم می‌تونن به تسک‌های تیم خودشون دسترسی داشته باشن.
    """

    def has_permission(self, request, view):
        team = None

        # ۱. اگر team در body وجود داشت
        team_id = request.data.get('team')
        if team_id:
            team = Team.objects.filter(id=team_id).first()

        # ۲. در غیر این صورت اگه pk در URL هست، تیم رو از تسک پیدا کن
        elif view.kwargs.get('pk'):
            task = Task.objects.filter(pk=view.kwargs['pk']).select_related('team').first()
            if task:
                team = task.team

        # ۳. در صورتی که team پیدا شد، بررسی کن که کاربر عضوش هست یا نه
        if team:
            return team.members.filter(id=request.user.id).exists()

        # اگر هیچ تیمی پیدا نشد، اجازه نده
        return False

    def has_object_permission(self, request, view, obj):
        # بررسی دسترسی در سطح شیء
        return obj.team.members.filter(id=request.user.id).exists()
