from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.shortcuts import get_object_or_404
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()

from chat.models import UserChat, UserChatThread


PERSONAL_MESSAGE = "personal_message"  # messages of user to other user person
LIKE_FOR_MESSAGE = "like"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            if str(self.user) == "AnonymousUser":
                try:
                    session_key = 'dsd'
                    user = await self.get_user_for_sessionid(session_key)
                    self.user = user
                except Exception as e:
                    print(e)
            if self.user.is_authenticated:
                self.room_group_name = "conn_%s" % self.user.id
                print(
                    self.room_group_name,
                )

                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )

                await self.accept()
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        print("leaving group")
    


    async def send_personal_message(self, text_data_json):
        message = text_data_json["message"]
        receiver_id = text_data_json["receiver_id"]
        chat_thread_id = text_data_json["id"]
        try:
            chat_message = await self.create_personal_message(
                message, self.user, receiver_id, chat_thread_id
            )
        except Exception as e:
            print(e)
        in_message_object_sender = {
            # type specifies which function to call in the current class
            # example --> type:abc calls the function abc
            "type": "user_personal_message",
            "message": chat_message.message,
            "sender": chat_message.sender_id,
            "receiver": chat_message.receiver_id,
            "event_type": "personal_message",
            "chat_thread": str(chat_message.chat_thread_id),
            "created": str(chat_message.created),
            "message_id": str(chat_message.id),
            "likes":chat_message.like
        }
        
        await self.channel_layer.group_send(
            self.room_group_name, in_message_object_sender
        )

    async def like_for_personal_message(self, text_data_json):
        message_ids = text_data_json["message_id"]
        chat_messages, sender_id = await self.update_personal_message(
            message_ids
        )
        chat_messages_dict_sender = {
            'type': 'user_personal_message_seen',
            'chat_messages': chat_messages,

        }
       
        try:
            await self.channel_layer.group_send(
                f"conn_{sender_id}", chat_messages_dict_sender
            )
        except Exception as e:
            print(e)

    # Receive message from WebSocket

    async def receive(self, text_data):
        try:
            if self.user.is_authenticated:
                # byte stream to json
                text_data_json = json.loads(text_data)
                msg_type = text_data_json["type"]
                if msg_type == PERSONAL_MESSAGE:
                    await self.send_personal_message(text_data_json)
                elif msg_type == LIKE_FOR_MESSAGE:
                    await self.like_for_personal_message(text_data_json)
        except Exception as e:
            print( e)

    # Receive message from room group

    async def chat_message(self, event):
        # event may be a notification or message
        message_object = {
            "event_type": event.get("event_type"),
            "message": event.get("message"),
            "chat_thread": event.get("chat_thread"),
            "sender": event.get("sender"),
        }
        await self.send(text_data=json.dumps(message_object))

    async def user_personal_message_seen(self, event):
        print(event)

        message_object = {
            "event_type": event.get("type"),
            "chat_thread": event['chat_messages'].get('chat_thread'),
            "message_id":event['chat_messages']['id']
        }
        await self.send(text_data=json.dumps(message_object))

    

        

    async def user_personal_message(self, event):
        message_object = {
            "event_type": event.get("event_type"),
            "message": event.get("message"),
            "sender": event.get("sender"),
            "created": event.get('created'),
            "chat_thread": event.get('chat_thread'),
            "id": event.get('message_id'),
        }
        await self.send(text_data=json.dumps(message_object))

    @database_sync_to_async
    def get_user_for_sessionid(self, sessionid):
       
        try:
            # from rest_framework.auth_token import Token
            # user = Token.objects.get(key=sessionid)

            # dummy testing 
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.first()
        except Exception as e:
            print( e)
            session = Session.objects.get(session_key=sessionid)
            session_data = session.get_decoded()
            # uid = session_data.get("_auth_user_id")
            return User.objects.first()

    @database_sync_to_async
    def create_personal_message(self, message, sender, receiver_id, chat_thread_id):
        chat_thread_obj = get_object_or_404(UserChatThread, id=chat_thread_id)
        receiver = get_object_or_404(User, pk=receiver_id)
        user_chat_message = UserChat(
            message=message,
            chat_thread=chat_thread_obj,
            sender=sender,
            receiver=receiver,
        )
        user_chat_message.save()

        return user_chat_message

    @database_sync_to_async
    def update_personal_message(self, message_id):
        sender_id = None
        message = get_object_or_404(UserChat, id=message_id)
        message_to_send = {}
        message.like = message.like+1
        message.save()
        sender_id = message.sender_id
        message_to_send['id'] = str(message.id)
        message_to_send['chat_thread'] = str(message.chat_thread_id)
        message_to_send["event_type"] = LIKE_FOR_MESSAGE
        message_to_send['like'] = message.like

        return message_to_send, sender_id
