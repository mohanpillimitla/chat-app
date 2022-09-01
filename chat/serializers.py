from re import search
from rest_framework import serializers
from chat.models import UserChat, UserChatThread

from authentication.models import User
from datetime import datetime





class UserChatThreadSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)

    class Meta:
        fields = '__all__'
        model = UserChatThread
        read_only_fields=('creation',)
    

    def create(self, validated_data):
        chat_thread = UserChatThread.objects.create()
        chat_thread.participant.set(validated_data.get('participant'))
        chat_thread.creation = datetime.now()
        chat_thread.save()
        return chat_thread


class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = UserChat

