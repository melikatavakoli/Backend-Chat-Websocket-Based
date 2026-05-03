import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message, ChatMembership
from .serializers import MessageSerializer
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        if not await self.is_member():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

        await self.update_last_seen()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'send_message':
            await self.handle_send_message(data)
        elif action == 'edit_message':
            await self.handle_edit_message(data)
        elif action == 'delete_message':
            await self.handle_delete_message(data)
        elif action == 'typing':
            await self.handle_typing(data)
        elif action == 'seen':
            await self.handle_seen(data)
        elif action == 'forward_message':
            await self.handle_forward_message(data)

    async def handle_send_message(self, data):
        content = data.get('content', '')
        media_file = data.get('media_file', None)
        media_type = data.get('media_type', None)
        reply_to_id = data.get('reply_to', None)
        
        message = await self.create_message(
            content=content,
            media_file=media_file,
            media_type=media_type,
            reply_to_id=reply_to_id
        )
        
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_full_name(),
                    'sent_at': str(message['sent_at'])
                }
            )
    
    async def handle_edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('content')
        
        message = await self.edit_message(message_id, new_content)
        
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': message_id,
                    'content': new_content,
                    'edited_at': str(timezone.now())
                }
            )
    
    async def handle_delete_message(self, data):
        message_id = data.get('message_id')
        
        if await self.delete_message(message_id):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id
                }
            )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'user_name': self.user.get_full_name(),
                'is_typing': is_typing
            }
        )
    
    async def handle_seen(self, data):
        message_id = data.get('message_id')
        
        await self.mark_message_as_seen(message_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_seen',
                'message_id': message_id,
                'user_id': self.user.id,
                'seen_at': str(timezone.now())
            }
        )
    
    async def handle_forward_message(self, data):
        message_id = data.get('message_id')
        target_chat_id = data.get('target_chat_id')
        
        result = await self.forward_message(message_id, target_chat_id)
        
        if result:
            await self.send(text_data=json.dumps({
                'action': 'forward_success',
                'message': result
            }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sent_at': event['sent_at']
        }))
    
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'action': 'message_edited',
            'message_id': event['message_id'],
            'content': event['content'],
            'edited_at': event['edited_at']
        }))
    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'action': 'message_deleted',
            'message_id': event['message_id']
        }))
    
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'action': 'user_typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))
    
    async def message_seen(self, event):
        await self.send(text_data=json.dumps({
            'action': 'message_seen',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'seen_at': event['seen_at']
        }))

    @database_sync_to_async
    def is_member(self):
        try:
            return ChatMembership.objects.filter(
                chat_id=self.chat_id,
                user=self.user,
                is_active=True
            ).exists()
        except:
            return False
    
    @database_sync_to_async
    def create_message(self, content, media_file, media_type, reply_to_id):
        try:
            chat = Chat.objects.get(id=self.chat_id)
            
            message = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=content,
                media_type=media_type,
                reply_to_id=reply_to_id
            )
            
            return MessageSerializer(message).data
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        try:
            message = Message.objects.get(id=message_id, sender=self.user)
            message.content = new_content
            message.is_edited = True
            message.save()
            return True
        except:
            return False
    
    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender == self.user or message.chat.is_user_admin(self.user):
                message.delete()
                return True
            return False
        except:
            return False
    
    @database_sync_to_async
    def mark_message_as_seen(self, message_id):
        try:
            membership = ChatMembership.objects.filter(
                chat_id=self.chat_id,
                user=self.user
            ).first()
            
            if membership:
                message = Message.objects.get(id=message_id)
                membership.last_read_message = message
                membership.save()
                return True
            return False
        except:
            return False
    
    @database_sync_to_async
    def forward_message(self, message_id, target_chat_id):
        try:
            original = Message.objects.get(id=message_id)
            target_chat = Chat.objects.get(id=target_chat_id)
            
            # چک کردن دسترسی
            if not target_chat.can_message(self.user):
                return None
            
            new_message = Message.objects.create(
                chat=target_chat,
                sender=self.user,
                content=original.content,
                media_file=original.media_file,
                media_type=original.media_type,
                forward_from=original
            )
            
            return MessageSerializer(new_message).data
        except:
            return None
    
    @database_sync_to_async
    def update_last_seen(self):
        try:
            membership = ChatMembership.objects.filter(
                chat_id=self.chat_id,
                user=self.user
            ).first()
            
            if membership:
                membership.last_seen = timezone.now()
                membership.save()
        except:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.group_name = f'user_{self.user.id}_notifications'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('action') == 'ping':
            await self.send(text_data=json.dumps({'action': 'pong'}))
    
    async def notify_new_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_message_notification',
            'chat_id': event['chat_id'],
            'chat_name': event['chat_name'],
            'message_preview': event['message_preview'],
            'sender_name': event['sender_name']
        }))
    
    async def notify_member_added(self, event):
        await self.send(text_data=json.dumps({
            'action': 'member_added',
            'chat_id': event['chat_id'],
            'chat_name': event['chat_name'],
            'added_by': event['added_by']
        }))
