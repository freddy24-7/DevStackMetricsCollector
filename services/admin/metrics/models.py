import uuid

from django.db import models

from nodes.models import Node


class Metric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="metrics")
    cpu_pct = models.DecimalField(max_digits=5, decimal_places=2)
    ram_pct = models.DecimalField(max_digits=5, decimal_places=2)
    disk_pct = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "metrics"
