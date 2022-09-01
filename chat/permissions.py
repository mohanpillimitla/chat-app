from rest_framework import permissions
from chat.models import UserChatThread

class IsChatParticipant(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        try:
            UserChatThread.object.get(id=view.kwargs.pk, participant__in= [request.user])
            return True
        except:
            return True