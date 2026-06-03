from django.contrib import admin
from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at", "revoked_at")
    readonly_fields = ("id", "key_hash", "created_at")
