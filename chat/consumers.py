import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.serializers import MessageRealtimeSerializer
from .models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        user = self.scope['user']
        voice_data = data.get('voice')

        if not message_text and not voice_data:
            return

        # بررسی اینکه کاربر عضو چت هست
        chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        if not await database_sync_to_async(chat.can_message)(user):
            return await self.close()

        # ذخیره پیام
        message_obj = await self.create_message(user, message_text, voice_data)

        # ارسال به گروه
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message_obj
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def create_message(self, user, message_text, voice_data):
        chat = Chat.objects.get(id=self.chat_id)
        msg = Message.objects.create(
            chat=chat,
            sender=user,
            content=message_text,
            voice=voice_data
        )
        return msg