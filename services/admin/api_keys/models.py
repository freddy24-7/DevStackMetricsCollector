import hashlib
import secrets
import uuid

from django.contrib.auth.models import User
from django.db import models


class ApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    key_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "api_keys"

    @property
    def is_active(self):
        return self.revoked_at is None

    @classmethod
    def generate(cls, user):
        raw_key = secrets.token_hex(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        instance = cls.objects.create(user=user, key_hash=key_hash)
        # raw_key returned once and never stored
        return instance, raw_key
