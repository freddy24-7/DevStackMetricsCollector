import os
import sys
import uuid

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/collector"))
os.environ.setdefault("DATABASE_URL", "postgres://x:x@localhost/x")

from app import MetricsPayload


class TestMetricsPayloadValidation:
    def _valid(self, **overrides):
        data = {
            "node_id": str(uuid.uuid4()),
            "cpu_pct": 42.0,
            "ram_pct": 55.5,
            "disk_pct": 10.1,
        }
        data.update(overrides)
        return data

    def test_valid_payload_parses(self):
        p = MetricsPayload.model_validate(self._valid())
        assert 0 <= p.cpu_pct <= 100

    def test_missing_node_id_raises(self):
        data = self._valid()
        del data["node_id"]
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(data)

    def test_cpu_pct_above_100_raises(self):
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(self._valid(cpu_pct=100.1))

    def test_cpu_pct_below_0_raises(self):
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(self._valid(cpu_pct=-0.1))

    def test_ram_pct_above_100_raises(self):
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(self._valid(ram_pct=101.0))

    def test_disk_pct_below_0_raises(self):
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(self._valid(disk_pct=-1.0))

    def test_invalid_node_id_raises(self):
        with pytest.raises(ValidationError):
            MetricsPayload.model_validate(self._valid(node_id="not-a-uuid"))

    def test_boundary_values_accepted(self):
        p = MetricsPayload.model_validate(self._valid(cpu_pct=0, ram_pct=100, disk_pct=0))
        assert p.cpu_pct == 0
        assert p.ram_pct == 100
