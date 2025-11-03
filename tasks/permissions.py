from rest_framework import permissions
from .models import Team

class IsTeamMember(permissions.BasePermission):
    """
    Only team members can access the Task.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            team_id = request.data.get('team')
            if not team_id:
                return False
            try:
                team = Team.objects.get(id=team_id)
                return request.user in team.members.all()
            except Team.DoesNotExist:
                return False
        return True  # For GET requests, object-level permission will handle access

    def has_object_permission(self, request, view, obj):
        return request.user in obj.team.members.all()
