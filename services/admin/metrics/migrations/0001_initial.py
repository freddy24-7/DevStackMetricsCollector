import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("nodes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Metric",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("node", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to="nodes.node")),
                ("cpu_pct", models.DecimalField(decimal_places=2, max_digits=5)),
                ("ram_pct", models.DecimalField(decimal_places=2, max_digits=5)),
                ("disk_pct", models.DecimalField(decimal_places=2, max_digits=5)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "metrics"},
        ),
    ]
