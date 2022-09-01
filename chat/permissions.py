from rest_framework import permissions
from chat.models import UserChatThread

class IsChatParticipant(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        try:
            UserChatThread.objects.get(id=view.kwargs['pk'], participant__in= [request.user.id])
            return True
        except Exception as e:
            return False