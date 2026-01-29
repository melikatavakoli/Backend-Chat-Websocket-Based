from typing import Any
from rest_framework import serializers
from authentication.serializers import GenericModelSerializer
from ticket.models import (
    Chat, 
    ChatMembership, 
    Message, 
    Profile, 
    )
from django.contrib.auth import get_user_model

User = get_user_model()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Profile Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "user",
            "avatar",
            "bio",
        )
        read_only_fields = fields
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Message Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MessageSerializer(serializers.ModelSerializer):
    sender_profile = ProfileSerializer(
        source='sender.profile_chat', 
        read_only=True
        )
    reply_to_detail = serializers.SerializerMethodField()
    forward_from_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = (
            "chat",
            "sender",
            "content",
            "voice",
            "reply_to",
            "is_edited",
            'sender_profile',
            'forward_from_detail',
            'reply_to_detail',
            "sent_at"
        )
        # read_only_fields = fields

    def get_reply_to_detail(self, obj):
        if obj.reply_to:
            return {
                "id": str(obj.reply_to.id),
                "sender": str(obj.reply_to.sender.id) if obj.reply_to.sender else None,
                "content": obj.reply_to.content,
            }
        return None

    def get_forward_from_detail(self, obj):
        if obj.forward_from:
            return {
                "id": str(obj.forward_from.id),
                "sender": str(obj.forward_from.sender.id) if obj.forward_from.sender else None,
                "content": obj.forward_from.content,
            }
        return None
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chat Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChatSerializer:
    member_count = serializers.SerializerMethodField()
    members = ProfileSerializer(
        source='membership_chat.user.profile_chat', 
        many=True, read_only=True
        )
    
    class Meta:
        model = Chat
        fields = (
            "id",
            "name",
            "chat_type",
            "creator",
            "is_active",
            "member_count",
            "members"
        )
        read_only_fields = fields

    def get_member_count(self, obj):
        return obj.active_memberships.count()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Members Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChatMembershipSerializer(serializers.ModelSerializerizer):
    class Meta:
        model = ChatMembership
        fields = (
            "chat",
            "user",
            "role",
            "is_active",
            "joined_at"
        )
        read_only_fields = fields
