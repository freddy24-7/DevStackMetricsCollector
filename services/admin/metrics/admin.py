from django.contrib import admin
from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("id", "node", "cpu_pct", "ram_pct", "disk_pct", "recorded_at")
    readonly_fields = ("id", "recorded_at")
