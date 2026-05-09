from django.contrib import admin
from .models import GenericModel


class GenericModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at_display",
        "updated_at_display",
        "_created_by",
        "_updated_by",
    )

    readonly_fields = (
        "id",
        "_created_by",
        "_updated_by",
        "_created_at",
        "_updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "id",
    )

    ordering = ("-created_at",)

    actions = ["restore_objects"]

    def get_queryset(self, request):
        # show even deleted objects
        qs = super().get_queryset(request)
        if hasattr(self.model, "all_objects"):
            return self.model.all_objects.all()
        return qs

    @admin.action(description="Restore selected objects")
    def restore_objects(self, request, queryset):
        restored = 0
        for obj in queryset:
            if getattr(obj, "is_deleted", False):
                obj.restore()
                restored += 1
        self.message_user(request, f"{restored} objects restored.")


