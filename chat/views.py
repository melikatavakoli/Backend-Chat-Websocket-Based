from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Chat, Message, ChatMembership
from .serializers import *
from .services import can_user_forward, can_user_edit

class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatDetailSerializer
    
    def get_queryset(self):
        return Chat.objects.filter(
            membership_chat__user=self.request.user,
            membership_chat__is_active=True
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatListSerializer
        if self.action == 'create':
            return ChatCreateSerializer
        return ChatDetailSerializer
    
    def perform_create(self, serializer):
        chat = serializer.save(creator=self.request.user)
        chat.create_creator_membership()
        if chat.chat_type != 'private':
            from .models import ChatSettings
            ChatSettings.objects.create(chat=chat)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = chat.chat_messages.all()[:50]
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        
        if not chat.can_message(request.user):
            return Response({'error': 'You cannot send message here'}, status=403)
        
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request, 'chat_id': chat.id}
        )
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message, context={'request': request}).data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        chat = self.get_object()
        members = chat.membership_chat.filter(is_active=True)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        chat = self.get_object()
        
        if not chat.is_user_admin(request.user):
            return Response({'error': 'Only admins can add members'}, status=403)
        
        serializer = AddMemberSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user = User.objects.get(id=user_id)
                chat.add_member(user, added_by=request.user)
                return Response({'status': 'member added'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        chat = self.get_object()
        user_id = request.data.get('user_id')
        
        if not chat.is_user_admin(request.user):
            return Response({'error': 'Only admins can remove members'}, status=403)
        
        try:
            user = User.objects.get(id=user_id)
            chat.remove_member(user)
            return Response({'status': 'member removed'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        chat = self.get_object()
        
        if chat.chat_type != 'channel':
            return Response({'error': 'Only channels support public join'}, status=400)
        
        if chat.settings and chat.settings.is_public:
            chat.subscribe_to_channel(request.user)
            return Response({'status': 'joined channel'})
        
        return Response({'error': 'Channel is private'}, status=403)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        chat = self.get_object()
        chat.remove_member(request.user)
        return Response({'status': 'left chat'})


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        return Message.objects.filter(chat__membership_chat__user=self.request.user)
    
    @action(detail=True, methods=['put'])
    def edit(self, request, pk=None):

        message = self.get_object()

        if message.sender != request.user:
            return Response({'error': 'You can only edit your own messages'}, status=403)
        
        content = request.data.get('content')
        if content:
            message.content = content
            message.is_edited = True
            message.save()
            return Response(MessageSerializer(message, context={'request': request}).data)
        
        return Response({'error': 'Content required'}, status=400)
    
    @action(detail=True, methods=['post'])
    def forward(self, request, pk=None):
        message = self.get_object()
        target_chat_id = request.data.get('chat_id')
        
        if not can_user_forward(message, request.user):
            return Response({'error': 'You cannot forward this message'}, status=403)
        
        try:
            target_chat = Chat.objects.get(id=target_chat_id)
            
            if not target_chat.can_message(request.user):
                return Response({'error': 'You are not a member of target chat'}, status=403)
            
            new_message = Message.objects.create(
                chat=target_chat,
                sender=request.user,
                content=message.content,
                media_file=message.media_file,
                media_type=message.media_type,
                forward_from=message
            )
            
            return Response(MessageSerializer(new_message, context={'request': request}).data, status=201)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Target chat not found'}, status=404)
    
    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        message = self.get_object()

        if message.sender == request.user or message.chat.is_user_admin(request.user):
            message.delete()
            return Response({'status': 'deleted'})
        
        return Response({'error': 'You cannot delete this message'}, status=403)