from time import timezone
from chat.models import ChatMembership, ChatPermission, ChatSettings

def create_creator_membership(self):
    if not self.creator:
        return
    ChatMembership.objects.get_or_create(chat=self, user=self.creator, defaults={'is_admin': True, 'is_active': True})

def add_member(self, user, added_by=None):
    membership, created = ChatMembership.objects.get_or_create(chat=self, user=user, defaults={'is_admin': False, 'is_active': True})
    if not created and not membership.is_active:
        membership.is_active = True
        membership.save(update_fields=['is_active'])

def remove_member(self, user):
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if not membership:
        return False
    membership.is_active = False
    membership.save(update_fields=['is_active'])
    return True

def can_remove_admin(self, user):
    admins = self.active_memberships.filter(is_admin=True)
    return not (admins.count() == 1 and admins.first().user == user)

def promote_to_admin(self, user):
    self.active_memberships.filter(user=user).update(is_admin=True)

def demote_admin(self, user):
    if self.can_remove_admin(user):
        self.active_memberships.filter(user=user).update(is_admin=False)

def can_message(self, user):
    return self.active_memberships.filter(user=user).exists()

def is_user_admin(self, user):
    return self.active_memberships.filter(user=user, is_admin=True).exists()

def get_user_role(self, user):
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if not membership:
        return None
    if user == self.creator:
        return 'creator'
    return membership.role if membership.role else ('admin' if membership.is_admin else 'member')
    
def can_user_send_media(self, user):
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if not membership:
        return False
    if self.is_channel:
        return membership.is_admin or membership.role == 'creator'
    if hasattr(self, 'settings') and not self.settings.can_send_media:
        return membership.is_admin or membership.role == 'creator'
    return membership.has_permission('send_media')
    
def can_user_forward(self, user, message):
    if not message.can_forward:
        return False
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if not membership:
        return False
    if message.sender == user:
        return True
    return membership.has_permission('forward_message')
    
def can_user_edit(self, user, message):
    if message.sender == user:
        return True
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if not membership:
        return False
    return membership.has_permission('edit_message')

def update_last_seen(self, user):
    membership = self.membership_chat.filter(user=user, is_active=True).first()
    if membership:
        membership.last_seen = timezone.now()
        membership.save(update_fieldss=['last_seen'])
    
def get_member_last_seen(self, target_user, requesting_user):
    membership = self.membership_chat.filter(user=target_user, is_active=True).first()
    if not membership:
        return None
    if requesting_user == target_user:
        return membership.last_seen
    if hasattr(self, 'settings') and self.settings.hide_last_seen:
        return None
    if membership.hide_last_seen_for_this_chat:
        return None
    return membership.last_seen

def create_channel(self, name, creator, username=None, is_public=True):
    self.name = name
    self.creator = creator
    self.chat_type = 'channel'
    self.username = username
    self.save()
    
    ChatSettings.objects.create(chat=self, only_admins_can_add_members=True, is_public=is_public, can_send_media=True, hide_members_list=not is_public)
    ChatMembership.objects.create(chat=self, user=creator, role='creator', is_admin=True, is_active=True)
    
    default_permissions = [
        ('subscriber', 'send_message', False),
        ('subscriber', 'send_media', False),
        ('subscriber', 'forward_message', True),
        ('admin', 'send_message', True),
        ('admin', 'send_media', True),
        ('admin', 'pin_message', True),
    ]
    
    for role, perm, allowed in default_permissions:
        ChatPermission.objects.create(chat=self, role=role, permission=perm, is_allowed=allowed)
        return self
    
def create_group(self, name, creator, is_private=False):
    self.name = name
    self.creator=creator
    self.chat_type='group'
    self.is_private=is_private
    self.save()
    
    ChatSettings.objects.create(chat=self, only_admins_can_add_members=False, can_send_medica=True, can_send_voice=True, slowe_mode=0)
    ChatMembership.objects.create(chat=self, user=creator, role='creator', is_admin=True, is_active=True)
    
    return self

def subscribe_to_channel(self, user):
    if not self.is_channel:
        return False
    
    membership, created=ChatMembership.objects.get_or_create(chat=self, user=user, defaults={
        'role': 'subscriber',
        'is_admin': False,
        'is_active': True
    })
    
    if not created and not membership.is_active:
        membership.is_active=True
        membership.role = ' subscriber'
        membership.save()
    
    if hasattr(self, 'settings'):
        self.settings.subscribers_count = self.membership_chat.filter(is_active=True).count()
        self.settings.save(update_fields=['subscribers_count'])
        return None
    
def can_user_forward(self, user):
    if not self.can_forward:
        return False
    return self.chat.can_user_forward(user, self)

def can_user_edit(self, user):
    return self.chat.can_user_edit(user, self)
