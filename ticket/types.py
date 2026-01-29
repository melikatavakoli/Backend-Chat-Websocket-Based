from django.db import models

class CHAT_TYPE_CHOICES(models.TextChoices):
    private = "private", "Private"
    group = "group", "Group"
    channel = "channel", "Channel"