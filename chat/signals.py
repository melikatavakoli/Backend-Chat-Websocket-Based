from mailbox import Message
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Ticket

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# @receiver(post_save, sender=Message)
# def chat_message_notification(sender, instance, created, **kwargs):
#     if created and instance.chat:
#         from notifications.models import Logs
#         # نوتیف برای همه اعضای چت به جز فرستنده
#         recipients = instance.chat.active_memberships.exclude(user=instance.sender)
#         for member in recipients:
#             Logs.objects.create(
#                 user=member.user,
#                 title=f"پیام جدید در چت {instance.chat.name}",
#                 description=instance.content[:100],
#                 type="CHAT_MESSAGE",
#                 related_chat=instance
#             )