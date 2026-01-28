from django.contrib.auth import get_user_model
from django.db import models

import jdatetime
from authentication.models import GenericModel
from notifications.models import Notifs
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

######### CHAT ######### 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Profile Model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Profile(GenericModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile_chat',
        verbose_name='user',
        null=True,
        blank=True
        )
    avatar = models.ImageField(
        'avatar',
        upload_to='upload_to_by_date', 
        blank=True, 
        null=True
        )
    bio = models.TextField(
        'bio',
        null=True,
        blank=True
        )

    class Meta:
        verbose_name = "03-profile"
        verbose_name_plural = "03-profile"
        db_table = 'profile'
        # ordering = ('-created_at',)
        
    def __str__(self):
        return self.user.get_full_name() if self.user else "Anonymous Profile"
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chat Model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Chat(GenericModel):
    name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # اگر کاربر حذف شد، چت باقی بماند
        related_name="created_chats",
        verbose_name="creator",
        blank=True, 
        null=True
    )
    is_active = models.BooleanField(
        'is_active',
        default=True
        )
    is_private = models.BooleanField(
        'is_private',
        default=True
        )
    chat_type = models.CharField(
        max_length=10, 
        choices=CHAT_TYPE_CHOICES, 
        default='private'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['creator', 'is_active']),
            # models.Index(fields=['created_at']),
        ]
        verbose_name = '04-chat'
        verbose_name_plural = '04-chats'
        db_table = 'chat'

    # -----------------------------------
    # Properties
    # -----------------------------------
    @property
    def active_memberships(self):
        return self.membership_chat.filter(is_active=True)

    @property
    def member_count(self):
        return self.active_memberships.count()

    @property
    def is_private(self):
        return self.member_count <= 2

    # -----------------------------------
    # Membership Management
    # -----------------------------------
    def create_creator_membership(self):
        """ایجاد ممبر اولیه (ادمین)"""
        if not self.creator:
            return

        ChatMembership.objects.get_or_create(
            chat=self,
            user=self.creator,
            defaults={
                'is_admin': True,
                'is_active': True
            }
        )

    def add_member(self, user, added_by=None):
        """
        اضافه کردن ممبر به چت. اگر کاربر قبلا عضو بود ولی غیرفعال شده بود، دوباره فعال می‌شود.
        """
        membership, created = ChatMembership.objects.get_or_create(
            chat=self,
            user=user,
            defaults={
                'is_admin': False,
                'is_active': True
            }
        )

        if not created and not membership.is_active:
            membership.is_active = True
            membership.save(update_fields=['is_active'])

        if added_by:
                Notifs.objects.create(
                    user=user,
                    title="دعوت به چت",
                    notif_type="chat",
                    description=f"{added_by.full_name} شما را به چت '{self.name}' دعوت کرد",

                    content_type=ContentType.objects.get_for_model(Chat),
                    object_id=self.id,
                )

        for member in self.active_memberships.exclude(user=user):
            Notifs.objects.create(
                user=member.user,
                title="عضو جدید",
                type="chat_member_added",
                description=f"{user.full_name or user.mobile} به چت '{self.name}' اضافه شد"
            )

        return True


    def remove_member(self, user):
        """
        غیرفعال کردن عضویت کاربر در چت.
        """
        membership = self.membership_chat.filter(user=user, is_active=True).first()
        if not membership:
            return False  # کاربر عضو فعال نیست

        membership.is_active = False
        membership.save(update_fields=['is_active'])

        Notifs.objects.create(
            user=user,
            title="حذف از چت",
            type="chat_removed",
            description=f"شما از چت '{self.name}' حذف شدید"
        )

        return True

    def can_remove_admin(self, user):
        admins = self.active_memberships.filter(is_admin=True)
        return not (admins.count() == 1 and admins.first().user == user)
    
    def promote_to_admin(self, user):
        self.active_memberships.filter(user=user).update(is_admin=True)
        
    def demote_admin(self, user):
        if self.can_remove_admin(user):
            self.active_memberships.filter(user=user).update(is_admin=False)
            
    # -----------------------------------
    # Permissions
    # -----------------------------------
    def can_message(self, user):
        return self.active_memberships.filter(user=user).exists()

    def is_user_admin(self, user):
        return self.active_memberships.filter(
            user=user,
            is_admin=True
        ).exists()

    # -----------------------------------
    def __str__(self):
        if self.is_private:
            return "چت خصوصی"
        return f"گروه ({self.member_count} عضو) - {self.name or 'بدون نام'}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chat-Membership Model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChatMembership(GenericModel):
    chat = models.ForeignKey(
        Chat, 
        on_delete=models.CASCADE, 
        related_name="membership_chat",
        verbose_name="chat",
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="chat_member",
        verbose_name="user",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        'is_active',
        default=True
        )
    is_admin = models.BooleanField(
        'is_admin',
        default=False
        )
    joined_at = models.DateTimeField(
        'joined_at',
        auto_now_add=True
        )

    class Meta:
        unique_together = ('chat', 'user')
        verbose_name = "05-member"
        verbose_name_plural = "05-members"
        db_table = 'member'
        
    def __str__(self):
        return f"{self.user.username} in {self.chat}"
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Message Model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Message(GenericModel):
    chat = models.ForeignKey(
        Chat, 
        verbose_name='message',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="chat_messages"
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True,
        null=True,
        verbose_name='sender',
        related_name="chat_sender"
    )
    content = models.TextField(
        'content',
        null=True, 
        blank=True
    )
    voice = models.BinaryField(
        'voice',
        blank=True, 
        null=True
        ) 
    sent_at = models.DateTimeField(
        'sent_at',
        auto_now_add=True
        )
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    forward_from = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='forwards'
    )
    is_edited = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sent_at']
        verbose_name = "06-chat_message"
        verbose_name_plural = "06-chat_messages"
        db_table = 'chat_message'
        
    def notify_chat_members(self):
        """
        ارسال نوتیفیکیشن به تمام اعضای چت
        به جز فرستنده پیام
        """
        if not self.chat or not self.sender:
            return

        members = self.chat.active_memberships.exclude(user=self.sender)

        for member in members:
            Notifs.objects.create(
                user=member.user,
                title="پیام جدید",
                description=(self.content or "")[:100],
                notif_type="chat",

                content_type=ContentType.objects.get_for_model(Message),
                object_id=self.id,
            )

    def __str__(self):
        return f"Message from {self.sender}"