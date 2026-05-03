from uuid import uuid4
from django.utils import timezone
from django_currentuser.middleware import get_current_authenticated_user
from django.db import models
from django_currentuser.db.models import CurrentUserField
from core.format import common_datetime_str, common_user_str
from core.models import User


def get_current_user_or_none():
    user = get_current_authenticated_user()
    if user and isinstance(user, User):
        return user
    return None

class GenericModel(models.Model):
    id = models.UUIDField(
        verbose_name="unique id",
        primary_key=True,
        unique=True,
        default=uuid4,
        editable=False
    )
    created_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=("created by"),
    )
    updated_by = CurrentUserField(
        related_name="%(app_label)s_%(class)s_updated_by",
        verbose_name=("updated by"),
        on_update=True
    )
    created_at = models.DateTimeField(
        verbose_name="created at",
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        verbose_name="updated at",
        auto_now=True
    )

    class Meta:
        abstract = True
        indexes = (
            models.Index(fields=['id'], name='%(class)s_id_idx'),
        )
        
    def save(self, *args, **kwargs):
        
        current_user = get_current_user_or_none()
        
        if not self.pk and not self.created_by:
            
            self.created_by = current_user
            
        self.updated_by = current_user
        
        super().save(*args, **kwargs)

    @property
    def _created_by(self):
        return common_user_str(self.created_by)

    @property
    def _updated_by(self):
        return common_user_str(self.updated_by)

    @property
    def _created_at(self):
        return common_datetime_str(self.created_at)

    @property
    def _updated_at(self):
        return common_datetime_str(self.updated_at)
