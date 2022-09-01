from django.db import models


from pyexpat import model
from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
User = get_user_model()

class UserChatThread(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    participant = models.ManyToManyField(
        User, related_name="participants", blank=False
    )
    creation = models.DateTimeField(
        null=True, auto_now=False, auto_now_add=False,blank=True)

    def __str__(self):
        return str(self.id)

   

class UserChat(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    message = models.CharField(null=False, max_length=2048)
    created = models.DateTimeField(
        null=False, auto_now=True, auto_now_add=False)
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="chat_message_sender", null=False
    )
    receiver = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="chat_message_receiver", null=False
    )
    chat_thread = models.ForeignKey(
        UserChatThread, on_delete=models.PROTECT, related_name="chat", null=False
    )
    like = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

   