from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, ChatMembership, Message
from .types import USER_ROLE

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ChatListSerializer(serializers.ModelSerializer):
    last_message = serializers.CharField(source='chat_messages.last.content', read_only=True)
    last_message_time = serializers.DateTimeField(source='chat_messages.last.sent_at', read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Chat
        fields = ['id', 'name', 'chat_type', 'is_private', 'last_message', 'last_message_time', 'unread_count']


class ChatDetailSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    user_role = serializers.SerializerMethodField()
    settings = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'name', 'chat_type', 'is_private', 'description', 'member_count', 'user_role', 'settings']
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_user_role(request.user)
        return None
    
    def get_settings(self, obj):
        if hasattr(obj, 'settings'):
            return {
                'only_admins_can_send': obj.settings.only_admins_can_send,
                'slow_mode': obj.settings.slow_mode,
                'description': obj.settings.description
            }
        return None


class ChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['name', 'chat_type', 'description', 'username']
    
    def validate_chat_type(self, value):
        if value not in ['private', 'group', 'channel']:
            raise serializers.ValidationError("Invalid chat type")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_forward = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'media_file', 'media_type', 
                'emoji', 'sent_at', 'is_edited', 'reply_to', 'can_edit', 'can_forward', 'media_url']
        read_only_fields = ['sender', 'sent_at', 'is_edited']
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.sender == request.user
        return False
    
    def get_can_forward(self, obj):
        return obj.can_forward
    
    def get_media_url(self, obj):
        if obj.media_file:
            return obj.media_file.url
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'media_file', 'media_type', 'emoji', 'reply_to']
    
    def create(self, validated_data):
        request = self.context.get('request')
        chat_id = self.context.get('chat_id')
        
        message = Message.objects.create(
            chat_id=chat_id,
            sender=request.user,
            **validated_data
        )
        return message


class MemberSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ChatMembership
        fields = ['user', 'user_info', 'role', 'is_admin', 'joined_at', 'last_seen']


class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=USER_ROLE.choices, default=USER_ROLE.MEMBER)
