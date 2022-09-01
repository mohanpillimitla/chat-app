from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404


# channels imports
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.models import UserChat, UserChatThread

from django.contrib.auth import get_user_model
from django.db.models import Prefetch


User = get_user_model()


@receiver(post_save, sender=UserChat)
def IdeaMessageBroadCast(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    # sending message to idea subscribers
    in_message_object_idea_subscribers = {
        # type specifies which function to call in the current class
        # example --> type:abc calls the function abc
        "type": "chat_message",
        "message": instance.message,
        "sender": instance.sender_id,
        "chat_thread": str(instance.chat_thread),
        "event_type": "chat_message",
        "likes": instance.like
    }
    participants_prefetch = Prefetch(
        "participant", User.objects.all().exclude(id=instance.sender.id))
    for chat_follower in UserChatThread.objects.filter(id=instance.chat_thread_id).prefetch_related(participants_prefetch).first().participant.all():
        # Send message to room group
        async_to_sync(channel_layer.group_send)(
            f"conn_{chat_follower.id}", in_message_object_idea_subscribers
        )
