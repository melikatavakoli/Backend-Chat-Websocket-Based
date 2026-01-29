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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Admin
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'title',
        'status',
        'priority',
        'is_active',
        'is_resolved',
        'created_by',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'is_active',
        'is_resolved',
    )
    search_fields = (
        'number',
        'title',
        'description',
    )
    ordering = ('-created_at',)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Detail Admin
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@admin.register(TicketDetail)
class TicketDetailAdmin(admin.ModelAdmin):
    list_display = (
        'ticket',
        'user',
        'created_at',
    )
    search_fields = (
        'ticket__number',
        'user__username',
        'message',
    )
    ordering = ('-created_at',)