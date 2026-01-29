from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from chat.models import (
    Chat, 
    Message, 
    Profile, 
    )
from chat.serializers import (
    ChatSerializer,
    MessageSerializer,
    ProfileSerializer, 
    )
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Profile ViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # فقط پروفایل‌هایی که کاربر فعال دارند یا می‌خوای همه رو بده
        return Profile.objects.all()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chat ViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # فقط چت‌هایی که کاربر عضو فعالش هست
        return Chat.objects.filter(
            membership_chat__user=self.request.user,
            membership_chat__is_active=True
        ).distinct()

    def perform_create(self, serializer):
        chat = serializer.save(creator=self.request.user)
        chat.create_creator_membership()

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        chat = self.get_object()
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        success = chat.add_member(user, added_by=request.user)
        return Response({"success": success})

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        chat = self.get_object()
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        success = chat.remove_member(user)
        return Response({"success": success})

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Message ViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # برای PATCH/PUT/DELETE فقط پیام خودش پیدا می‌شود
        queryset = Message.objects.filter(
            chat__membership_chat__user=self.request.user,
            chat__membership_chat__is_active=True
        ).order_by('sent_at')

        # اگر query param chat مشخص شد، فقط پیام‌های آن چت را برمی‌گرداند
        chat_id = self.request.query_params.get('chat')
        if chat_id:
            queryset = queryset.filter(chat__id=chat_id)

        return queryset

    def perform_create(self, serializer):
        chat = serializer.validated_data['chat']
        if not chat.can_message(self.request.user):
            raise PermissionDenied("اجازه ارسال پیام ندارید")
        serializer.save(sender=self.request.user)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Message Create View
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.can_message(self.request.user):
            raise PermissionDenied("اجازه ارسال پیام ندارید")

        serializer.save(sender=self.request.user, chat=chat)