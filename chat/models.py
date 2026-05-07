from django.contrib.auth import get_user_model
from django.db import models
from chat.types import CHAT_TYPE, MESSAGE_PERMISSION, USER_ROLE, MediaType
from core.models import GenericModel
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Profile(GenericModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_chat', verbose_name='user', null=True, blank=True)
    avatar = models.ImageField('avatar', upload_to='upload_to_by_date', blank=True, null=True)
    bio = models.TextField('bio', null=True, blank=True)
    mobile = models.CharField(max_length=12, null=True, blank=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profile"
        db_table = 'profile'

    def __str__(self):
        return self.user.get_full_name() if self.user else "Anonymous Profile"


class Chat(GenericModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="created_chats", verbose_name="creator", blank=True, null=True)
    is_active = models.BooleanField('is_active', default=True)
    is_private = models.BooleanField('is_private', default=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE, default='private')
    username = models.CharField('channel username', max_length=100, blank=True, null=True, unique=True)
    description = models.TextField('description', blank=True, null=True)
    
    class Meta:
        indexes = [models.Index(fields=['creator', 'is_active'])]
        verbose_name = 'chat'
        verbose_name_plural = 'chats'
        db_table = 'chat'

    @property
    def is_channel(self):
        return self.chat_type == 'channel'
    
    @property
    def is_group(self):
        return self.chat_type == 'group'

    @property
    def can_members_send_message(self):
        if self.is_channel:
            return False
        if self.is_private:
            return True
        return not self.settings.only_admins_can_send if hasattr(self, 'settings') else True
    
    @property
    def active_memberships(self):
        return self.membership_chat.filter(is_active=True)

    @property
    def member_count(self):
        return self.active_memberships.count()

    @property
    def is_chat_private(self):
        return self.member_count <= 2

    def __str__(self):
        if self.is_chat_private:
            return "چت خصوصی"
        return f"گروه ({self.member_count} عضو) - {self.name or 'بدون نام'}"


class ChatMembership(GenericModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="membership_chat", verbose_name="chat", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_member", verbose_name="user", blank=True, null=True)
    is_active = models.BooleanField('is_active', default=True)
    is_admin = models.BooleanField('is_admin', default=False)
    role = models.CharField(max_length=20, choices=USER_ROLE, default='member')
    joined_at = models.DateTimeField('joined_at', auto_now_add=True)
    last_seen = models.DateTimeField('last seen', blank=True, null=True)
    last_read_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name="read_by_members")
    muted_until = models.DateTimeField('muted until', blank=True, null=True)
    nickname = models.CharField('nickname', max_length=100, blank=True, null=True)
    pinned_messages = models.ManyToManyField('Message', blank=True, related_name="pinned_by_members")
    hide_last_seen_for_this_chat = models.BooleanField('hide last seen for this chat', default=False)
    
    class Meta:
        unique_together = ('chat', 'user')
        verbose_name = "05-member"
        verbose_name_plural = "05-members"
        db_table = 'member'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} in {self.chat}"

    def has_permission(self, permissions_code):
        if self.role == 'creator':
            return True
        if self.role == 'admin' and permissions_code in ['add_member', 'remove_member', 'change_info', 'change_info', 'pin_message']:
            return True
        return ChatPermission.objects.filter(chat=self.chat, role=self.role, permission=permissions_code, is_allowed=True
        ).exits()

        
class Message(GenericModel):
    chat = models.ForeignKey(Chat, verbose_name='message', on_delete=models.CASCADE, blank=True, null=True, related_name="chat_messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='sender', related_name="chat_sender")
    content = models.TextField('content', null=True, blank=True)
    voice = models.BinaryField('voice', blank=True, null=True)
    sent_at = models.DateTimeField('sent_at', auto_now_add=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    forward_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forwards')
    is_edited = models.BooleanField(default=False)
    can_forward = models.BooleanField(default=True)
    last_message = models.ForeignKey("chat.Message", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    last_message_at = models.DateTimeField(null=True, blank=True)
    media_file = models.FileField('media file', upload_to='chat_media/%Y/%m/%d', blank=True, null=True)
    media_type = models.CharField('media type', max_length=20, blank=True, null=True, choices=MediaType)
    emoji = models.CharField('emoji', max_length=50, blank=True, null=True)
    forwarded_from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="forwarded_messages")
    forwarded_from_chat = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True, blank=True, related_name="forwarded_messages")
    view_count = models.IntegerField('view count', default=0)
    pin_expiry = models.DateTimeField('pin expiry', blank=True, null=True)
    
    class Meta:
        ordering = ['sent_at']
        verbose_name = "06-chat_message"
        verbose_name_plural = "06-chat_messages"
        db_table = 'chat_message'
        
    def __str__(self):
        return f"Message from {self.sender}"

        
class ChatPermission(GenericModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="permissions")
    role = models.CharField(max_length=20, choices=USER_ROLE, default='member')
    permission = models.CharField(max_length=50, choices=MESSAGE_PERMISSION)
    is_allowed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('chat', 'role', 'permission')
        db_table = 'chat_permission'
        verbose_name = "chat permission"
        verbose_name_plural = "chat permissions"

    def __str__(self):
        return f"{self.get_role_display()} - {self.get_permission_display()}: {self.is_allowed}"


class ChatSettings(GenericModel):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name="settings")
    description = models.TextField('description', blank=True, null=True)
    username = models.CharField('username', max_length=100, blank=True, null=True, unique=True)
    invite_link = models.CharField('invite link', max_length=255, blank=True, null=True)
    slow_mode = models.IntegerField('slow mode (seconds)', default=0) 
    only_admins_can_send = models.BooleanField('only admins can send', default=False) 
    only_admins_can_add_members = models.BooleanField('only admins can add members', default=False)
    only_admins_can_pin = models.BooleanField('only admins can pin', default=True)
    can_send_media = models.BooleanField('can send media', default=True)
    can_send_voice = models.BooleanField('can send voice', default=True)
    is_public = models.BooleanField('is public channel', default=True)
    subscribers_count = models.IntegerField('subscribers count', default=0)
    hide_members_list = models.BooleanField('hide members list', default=False)
    hide_last_seen = models.BooleanField('hide last seen', default=False)
    
    class Meta:
        db_table = 'chat_settings'
        verbose_name = "chat settings"
        verbose_name_plural = "chat settings"

    def __str__(self):
        return f"Settings for {self.chat.name or self.chat.id}"
