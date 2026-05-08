from uuid import uuid4
from django.utils import timezone
from django_currentuser.middleware import get_current_authenticated_user
from django.db import models
from django_currentuser.db.models import CurrentUserField
from django.db.models.deletion import ProtectedError
from functools import cached_property
from common.managers import SoftDeleteManager
from common.format import common_datetime_str, common_user_str
from django.contrib.auth import get_user_model

User = get_user_model()

def get_current_user_or_none():
    user = get_current_authenticated_user()
    if user and isinstance(user, User):
        return user
    return None

class GenericModel(models.Model):
    id = models.UUIDField(verbose_name="unique id", primary_key=True, unique=True, default=uuid4, editable=False)
    created_by = CurrentUserField(related_name="%(app_label)s_%(class)s_created_by", verbose_name="created by")
    updated_by = CurrentUserField(related_name="%(app_label)s_%(class)s_updated_by", verbose_name="updated by", on_update=True)
    created_at = models.DateTimeField(verbose_name="created at", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)
    objects = SoftDeleteManager(alive_only=True)
    all_objects = SoftDeleteManager(alive_only=None)
    deleted_objects = SoftDeleteManager(alive_only=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
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

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add("updated_by")
            kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)

    @classmethod
    def get_or_restore(cls, defaults=None, **kwargs):
        instance = cls.all_objects.filter(**kwargs).first()
        if instance:
            restored = False
            if instance.is_deleted:
                instance.restore()
                restored = True
            if defaults:
                for key, value in defaults.items():
                    setattr(instance, key, value)
                instance.save(update_fields=list(defaults.keys()))
            return instance, False, restored
        
        instance, created = cls.objects.get_or_create(defaults=defaults, **kwargs)
        return instance, created, False

    @classmethod
    def update_or_restore(cls, defaults=None, **kwargs):
        instance = cls.all_objects.filter(**kwargs).first()
        if instance:
            restored = False
            if instance.is_deleted:
                instance.restore()
                restored = True
            if defaults:
                for key, value in defaults.items():
                    setattr(instance, key, value)
                instance.save(update_fields=list(defaults.keys()))
            return instance, False, restored
        
        instance, created = cls.objects.update_or_create(defaults=defaults, **kwargs)
        return instance, created, False

    def delete(self, using=None, keep_parents=False):
        if self.is_deleted:
            return
        self._soft_delete_related(using=using)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        if not self.is_deleted:
            return
    
        for rel in self._meta.related_objects:
            if getattr(rel, "on_delete", None) is not models.CASCADE:
                continue
            
            try:
                related = getattr(self, rel.get_accessor_name())
            except Exception:
                continue
            
            if rel.one_to_one:
                try:
                    related.restore()
                except rel.related_model.DoesNotExist:
                    pass
            else:
                for obj in related.all():
                    obj.restore()
        
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def _soft_delete_related(self, using=None):
        for rel in self._meta.related_objects:
            on_delete = getattr(rel, "on_delete", None)
            if on_delete not in (models.CASCADE, models.SET_NULL, models.PROTECT):
                continue
            
            try:
                related = getattr(self, rel.get_accessor_name())
            except Exception:
                continue
            
            if on_delete is models.PROTECT:
                if rel.one_to_one:
                    if related:
                        raise ProtectedError("Cannot delete due to protected objects.", [related])
                elif related.all().exists():
                    raise ProtectedError("Cannot delete due to protected objects.", list(related.all()))
                continue
            
            if on_delete is models.SET_NULL:
                field_name = rel.field.name
                if rel.one_to_one:
                    if related:
                        setattr(related, field_name, None)
                        related.save(using=using, update_fields=[field_name])
                else:
                    related.all().update(**{field_name: None})
                continue
            
            if rel.one_to_one:
                try:
                    related.delete(using=using)
                except rel.related_model.DoesNotExist:
                    pass
            else:
                for obj in related.all():
                    obj.delete(using=using)

    @cached_property
    def can_delete(self):
        for rel in self._meta.related_objects:
            try:
                if getattr(self, rel.related_name).all().exists():
                    return False
            except Exception:
                pass
        return True

    @property
    def created_at_display(self):
        return common_datetime_str(self.created_at)

    @property
    def updated_at_display(self):
        return common_datetime_str(self.updated_at)
    
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