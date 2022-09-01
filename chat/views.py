from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated

# Create your views here.

from rest_framework.viewsets import ModelViewSet,ViewSet

from chat.models import UserChatThread,UserChat
from .serializers import UserChatSerializer, UserChatThreadSerializer
from rest_framework.response import Response
from .permissions import IsChatParticipant

class ChatThreadViewSet(ModelViewSet):
    serializer_class = UserChatThreadSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UserChatThread.objects.none()

    def get_queryset(self):
        if self.action=="list":
            return UserChatThread.objects.filter(participant__in=[self.request.user])
        return super().get_queryset()



class ChatViewSet(ViewSet):
    serializer_class = UserChatSerializer
    permission_classes = (IsAuthenticated,IsChatParticipant)
    queryset = UserChat.objects.all()

    def retrieve(self,request,pk):
        queryset = UserChat.objects.filter(chat_thread=pk)
        serializer = UserChatSerializer(queryset,many=True)
        return Response(serializer.data)


        




