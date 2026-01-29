from django.contrib import admin
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from .models import (
    Ticket,
    TicketDetail,
    Profile,
    Chat,
    ChatMembership,
    Message
)

@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    list_display = (
        'user',
        'created_at',
    )
    search_fields = (
        'user__username',
        'user__email',
    )
    ordering = ('-created_at',)
    
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'creator',
        'member_count',
        'is_active',
        'created_at',
    )
    search_fields = (
        'name',
        'creator__username',
    )
    ordering = ('-created_at',)

@admin.register(ChatMembership)
class ChatMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'chat',
        'user',
        'is_admin',
        'is_active',
        'joined_at',
    )
    list_filter = (
        'is_admin',
        'is_active',
    )
    search_fields = (
        'user__username',
        'chat__name',
    )
    ordering = ('-joined_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'chat',
        'sender',
        'is_edited',
        'sent_at',
    )
    search_fields = (
        'sender__username',
        'content',
    )
    ordering = ('-sent_at',)


