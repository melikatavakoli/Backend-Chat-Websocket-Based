from django.db import models

class CHAT_TYPE(models.TextChoices):
    PRIVATE = "private", "Private"
    GROUP = "group", "Group"
    CHANNEL = "channel", "Channel"

class USER_ROLE(models.TextChoices):
    MEMBER = "member", "Member"
    ADMIN = "admin", "Admin"
    CREATOR = "creator", "Creator"
    SUBSCRIBER = "subscriber", "Subscriber"

class MESSAGE_PERMISSION(models.TextChoices):
    SEND_MESSAGE = "send_message", "Send Message"
    SEND_MEDIA = "send_media", "Send Media"
    SEND_VOICE = "send_voice", "Send Voice"
    EDIT_MESSAGE = "edit_message", "Edit Message"
    DELETE_MESSAGE = "delete_message", "Delete Message"
    FORWARD_MESSAGE = "forward_message", "Forward Message"
    PIN_MESSAGE = "pin_message", "Pin Message"
    ADD_MEMBER = "add_member", "Add Member"
    REMOVE_MEMBER = "remove_member", "Remove Member"
    CHANGE_INFO = "change_info", "Change Info"
    CHANGE_SETTINGS = "change_settings", "Change Settings"

class MediaType(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    DOCUMENT = "document", "Document"
    VOICE = "voice", "Voice"
    STICKER = "sticker", "Sticker"
    GIF = "gif", "GIF"