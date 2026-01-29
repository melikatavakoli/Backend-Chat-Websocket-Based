from typing import Any
from rest_framework import serializers
from ticket.models import (
    Chat, 
    ChatMembership, 
    Message, 
    Profile, 
    Ticket, 
    TicketDetail
    )
from django.contrib.auth import get_user_model
from persiantools.jdatetime import JalaliDateTime

User = get_user_model()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User Ticket Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserTicketSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ticket
        fields = (
            'id',
            'category',
            'number',
            'title',
            'priority',
            # 'created_at',
        )

    def create(self, validated_data):
        user = self.context['request'].user

        if Ticket.objects.filter(user=self.context['request'].user).exclude(user=self.context['request'].user, category='O').count() > 15:
            return serializers.ValidationError({'ticket': 'شما می‌توانید تنها ۱۵ تیکت فعال داشته باشید!'})
        
        if Ticket.objects.filter(user=user).exclude(category='O').count() > 15:
            raise serializers.ValidationError(
                {'ticket': 'شما می‌توانید تنها ۱۵ تیکت فعال داشته باشید!'}
            )
    
        category = validated_data.get('category')
        title = validated_data.get('title')
        message = self.context['request'].data.get('message')
        attachment = self.context['request'].data.get('attachment')

        ticket = Ticket.objects.create(
            category=category,
            user=user,
            title=title,
        )

        TicketDetail.objects.create(
            ticket=ticket,
            message=message,
            attachment=attachment
        )
        return ticket

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField(required=False)
    user = serializers.SerializerMethodField(required=False)
    reviewer = serializers.SerializerMethodField(required=False)
    ticket_details = serializers.SerializerMethodField(required=False, read_only=True)
    is_reviewer = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            'id',
            'category',
            'user',
            'number',
            'title',
            'status_display',
            'status',
            'is_resolved',
            'reviewer',
            'can_reply',
            'can_upload_attachment',
            'ticket_details',
            'is_reviewer',
        )

    def get_status_display(self, obj) -> str :
        return obj.get_status_display()

    def get_user(self, obj) -> dict[str, Any] | None:
        if not obj.user:
            return None 
            
        data = {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'base_role': obj.user.base_role,
            'is_active': obj.user.is_active
        }
        return data

    def get_reviewer(self, obj) -> list[dict[str, Any]] | None:
        if obj.reviewer:
            reviewer_data = {
                'id': obj.reviewer.id,
                'first_name': obj.reviewer.first_name,
                'last_name': obj.reviewer.last_name,
                'mobile': obj.reviewer.mobile,
            }
            return reviewer_data
        else:
            return ''

    def get_ticket_details(self, obj) -> list[dict[str, Any]] | None:
        if obj.ticket.all():
            return TicketDetailSerializer(obj.ticket.all(), many=True).data
        return None

    def get_is_reviewer(self, obj) -> bool:
        if self.context['request'].user == obj.reviewer:
            return True
        return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Detail Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketDetailSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField(required=False)
    is_resolved = serializers.SerializerMethodField()

    class Meta:
        model = TicketDetail
        fields = (
            'id',
            'title',
            'user',
            'ticket',
            'is_resolved',
            'attachment',
            'message',
        )

    def get_user(self, obj) -> dict[str, Any] | None:
        if not obj.user:
            return None 
            
        data = {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'base_role': obj.user.base_role,
            'is_active': obj.user.is_active
        }
        return data

    def get_is_resolved(self, obj):
        return obj.ticket.is_resolved if obj.ticket else None

    def get_title(self, obj):
        return obj.ticket.title if obj.ticket else None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Detail Response Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketDetailResponseSerializer(serializers.Serializer):
    title_ticket = serializers.CharField()
    number_ticket = serializers.CharField()
    status_ticket = serializers.CharField()
    _created_by = serializers.CharField()
    reviewer_ticket = serializers.CharField()
    category_ticket = serializers.CharField()
    details = TicketDetailSerializer(many=True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Ticket Detail Serializer   
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CreateTicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketDetail
        fields = (
            'ticket',
            'attachment',
            'message',
            'id'
        )

    def create(self, validated_data):
        
        ticket = self.context['request'].data.get('ticket')
        message = validated_data.get('message')
        attachment = validated_data.get('attachment')
        
        ticket_detail = TicketDetail.objects.create(
            user=self.context['request'].user,
            ticket_id=ticket,
            message=message,
            attachment=attachment
        )
        
        return ticket_detail

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Write Ticket Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class WriteTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'category',
            'user',
            'number',
            'title',
            'priority',
            'status',
            'is_resolved',
            'can_reply',
            'can_upload_attachment',
        )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Write Ticket Detail Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class WriteTicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketDetail
        fields = [
            'user',
            'ticket',
            'attachment',
            'content'
        ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin Ticket Serializers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminEditTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'status',
            'is_resolved',
            'can_reply',
            'can_upload_attachment',
            'reviewer'
        )

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.is_resolved = validated_data.get('is_resolved', instance.is_resolved)
        instance.can_reply = validated_data.get('can_reply', instance.can_reply)
        instance.can_upload_attachment = validated_data.get(
            'can_upload_attachment',
            instance.can_upload_attachment
        )
        instance.reviewer = validated_data.get('reviewer', instance.reviewer)
        instance.save()
        return instance

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Reviewer List Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketReviewerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'base_role'
        )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin Create Ticket Serializer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminCreateTicketSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            'id',
            'user', 
            'category',
            'title',
            'reviewer',
            'status',
        )

    def get_user(self, obj) -> dict[str, Any] | None:
        if not obj.user:
            return None 
            
        data = {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'base_role': obj.user.base_role,
            'is_active': obj.user.is_active
        }
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user_id = request.data.get("user")
        if isinstance(user_id, dict): 
            user_id = user_id.get("id")
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                validated_data["user"] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"user": "User not found."})

        ticket = Ticket.objects.create(**validated_data)

        # --------- ایجاد دیتیل تیکت ---------
        message = request.data.get('message')
        detail_attachment = request.data.get('attachment')

        if message or detail_attachment:
            TicketDetail.objects.create(
                user=user or request.user,   # اگر ادمین به‌جای کاربر تیکت بسازه
                ticket=ticket,
                message=message,
                attachment=detail_attachment
            )
        return ticket