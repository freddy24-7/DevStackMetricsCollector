from django.contrib import admin
from .models import Node


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "hostname", "label", "created_at")
    readonly_fields = ("id", "created_at")
